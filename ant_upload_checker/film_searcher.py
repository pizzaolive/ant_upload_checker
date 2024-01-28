import pandas as pd
import requests
import logging
from ratelimit import limits, sleep_and_retry
from ant_upload_checker.parameters import API_KEY
import re
from requests.adapters import HTTPAdapter, Retry


class FilmSearcher:
    def __init__(self, film_list_df, api_key):
        self.film_list_df = film_list_df
        self.api_key = api_key
        self.session = requests.Session()

        retries = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def check_if_films_exist_on_ant(self):
        """
        Given pandas DataFrame of film list, if list contains
        films that already contain a torrentid from previous output file,
        then skip these films. For any not found, or new films in the list,
        search for these on ANT, indicating whether they exist on ANT or not.
        """
        films_to_skip = self.film_list_df.loc[
            self.film_list_df["Already on ANT?"]
            .astype(str)
            .str.contains("torrentid", regex=True)
        ]
        if not films_to_skip.empty:
            logging.info(
                "Skipping %s films already found on ANT in the previous output file...",
                len(films_to_skip),
            )

        films_to_process = (
            self.film_list_df.drop(films_to_skip.index)
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )
        films_to_process["API response"] = films_to_process["Parsed film title"].apply(
            self.check_if_film_exists_on_ant
        )

        processed_films = self.process_api_responses(films_to_process).drop(
            "API response", axis=1
        )

        films_checked_on_ant = (
            pd.concat([films_to_skip, processed_films])
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )

        return films_checked_on_ant

    def process_api_responses(self, films_to_process_with_api_responses):
        processed_films = films_to_process_with_api_responses.copy()
        processed_films["Already on ANT?"] = processed_films.apply(
            lambda x: self.check_if_resolution_exists_on_ant(
                x["Resolution"], x["API response"]
            ),
            axis=1,
        )

        return processed_films

    def check_if_resolution_exists_on_ant(self, film_resolution, api_response):
        if api_response == "NOT FOUND":
            return api_response

        if film_resolution == "":
            return (
                "On ANT, but could not get resolution from file name: "
                f"{api_response[0]['guid']}"
            )

        for match in api_response:
            if match["resolution"] == film_resolution:
                return f"Resolution already uploaded: {match['guid']}"

        return f"On ANT, but this resolution is missing from ANT"

    def check_if_film_exists_on_ant(self, film_title):
        """
        Take a film title, and search for it using the ANT API.
        If an initial match is not found, re-search for a
        modified version of the film title if it meets certain conditions.
        """
        logging.info("Searching for %s...", film_title)
        title_checks = [
            (self.search_for_film_title_on_ant, ""),
            (self.search_for_film_if_contains_and, ""),
            (self.search_for_film_if_contains_potential_date_or_time, "time"),
            (self.search_for_film_if_contains_potential_date_or_time, "date"),
        ]
        for search_function, optional_argument in title_checks:
            if optional_argument:
                search_result = search_function(film_title, optional_argument)
            else:
                search_result = search_function(film_title)
            if search_result != "NOT FOUND":
                return search_result

        logging.info("--- Not found on ANT ---\n")

        return search_result

    def search_for_film_if_contains_and(self, film_title):
        """
        If film title contains and or &, replace with the oppposite
        and search for the new title on ANT. Else, return NOT FOUND.
        """
        and_word_regex = r"(?i)\sand\s"
        and_symbol_regex = r"(?i)\s&\s"

        if re.search(and_word_regex, film_title):
            logging.info("-- Film contains 'and'.")
            return self.replace_word_and_re_search(film_title, and_word_regex, " & ")
        elif re.search(and_symbol_regex, film_title):
            logging.info("-- Film contains '&'.")
            return self.replace_word_and_re_search(
                film_title, and_symbol_regex, " and "
            )

        return "NOT FOUND"

    def search_for_film_if_contains_potential_date_or_time(self, film_title, format):
        """
        If film title 4 numbers e.g. 1208 East of Bucharest,
        add colon in middle, re-search title on ANT.
        Else, return NOT FOUND.
        """
        if format == "time":
            numbers_regex = r"(?<=\b\d\d)(?=\d\d\b)"
            replacement_value = ":"
        elif format == "date":
            numbers_regex = r"(?<=\b\d)(?=\d{1,2}\b)"
            replacement_value = "/"
        else:
            raise ValueError("The format argument must be 'time' or 'date'")

        if re.search(numbers_regex, film_title):
            logging.info(
                "-- Film title may contain a date or time without punctuation."
            )
            return self.replace_word_and_re_search(
                film_title, numbers_regex, replacement_value
            )

        return "NOT FOUND"

    @sleep_and_retry
    @limits(calls=1, period=2)
    def search_for_film_title_on_ant(self, film_title):
        """
        Use the ANT API to search for a film title and
        return the first URL if found, else a NOT FOUND string
        """
        url = "https://anthelion.me/api.php"

        if API_KEY == "":
            raise ValueError("The API_KEY must be set in parameters.py")

        payload = {
            "api_key": API_KEY,
            "q": film_title,
            "t": "movie",
            "o": "json",
        }

        response = self.session.get(url, params=payload)
        try:
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.HTTPError as err:
            logging.error(
                "HTTP Error: %s",
                err,
            )
            if response.status_code == 429:
                logging.error(
                    "Try increasing the API search period limit to greater than 2"
                )
            elif response.status_code == 403:
                logging.error(
                    "Your API key may be invalid. Check the key in parameters.py"
                )
            raise SystemExit(err)
        except requests.exceptions.ConnectionError as err:
            logging.error("Connection error despite retries, exiting process\n")
            raise SystemExit(err)
        except requests.exceptions.Timeout as err:
            logging.error("Timeout error despite retires, exiting process\n")
            raise SystemExit(err)
        except requests.exceptions.RequestException as err:
            logging.error("The following error occured: %s", err)
            raise SystemExit(err)

        if response_json["response"]["total"] == 0:
            return "NOT FOUND"
        else:
            return response_json["item"]

    def replace_word_and_re_search(self, film_title, regex_pattern, replacement):
        cleaned_film_title = re.sub(
            regex_pattern,
            replacement,
            film_title,
        )
        logging.info("-- Searching for %s as well...\n", cleaned_film_title)
        film_check = self.search_for_film_title_on_ant(cleaned_film_title)

        return film_check
