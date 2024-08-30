import pandas as pd
import requests
import logging
from pathlib import Path
from typing import Any, Union
from ratelimit import limits, sleep_and_retry
import re
from requests.adapters import HTTPAdapter, Retry


class FilmSearcher:
    def __init__(self, film_list_df: pd.DataFrame, api_key: str):
        self.film_list_df: pd.DataFrame = film_list_df
        self.api_key: str = api_key
        self.ant_url = "https://anthelion.me/api.php"
        self.session: requests.Session = requests.Session()
        self.not_found_value: str = "NOT FOUND"
        self.guid_missing_message = "(Failed to extract URL from API response)"

        retries = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def check_if_films_exist_on_ant(self) -> pd.DataFrame:
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

        processed_films = self.check_if_films_can_be_uploaded(films_to_process).drop(
            "API response", axis=1
        )

        films_checked_on_ant = (
            pd.concat([films_to_skip, processed_films])
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )

        return films_checked_on_ant

    def perform_partial_dupe_check(
        self, dupe_properties: dict[str, str], api_response: list[dict[str, Any]]
    ):
        properties_to_check = {k: v for k, v in dupe_properties if v}

        """
        Can definitely just condense this into one function with full dupe check
        
        """

        for existing_upload in api_response:
            existing_guid = existing_upload.get("guid", self.guid_missing_message)

            is_partial_duplicate = all(
                properties_to_check[prop] == existing_upload.get(prop)
                for prop in properties_to_check
            )
            if is_partial_duplicate:
                return (
                    f"Partial dupe check: a film with {'/'.join(properties_to_check)} exists, "
                    " but could not get other film properties from file name."
                )

    def perform_full_dupe_check(
        self, dupe_properties: dict[str, str], api_response: list[dict[str, Any]]
    ):
        dupe_property_values = "/".join(dupe_properties.values())

        for existing_upload in api_response:
            existing_guid = existing_upload.get("guid", self.guid_missing_message)

            is_duplicate = all(
                dupe_properties[property] == existing_upload.get(property, "")
                for property in dupe_properties
            )
            if is_duplicate:
                return f"Duplicate - a film with the same properties ({dupe_property_values}) already exists: {existing_guid}"

        return f"Not a duplicate - a film with {(dupe_property_values)} does not exist already"

    def check_remaining_dupe_properties(
        self,
        resolution: str,
        codec: str,
        source: str,
        api_response: list[dict[str, Any]],
    ) -> str:

        dupe_properties = {"resolution": resolution, "codec": codec, "source": source}
        missing_properties = [k for k, v in dupe_properties.items() if not v]

        if missing_properties:
            if len(missing_properties) == len(dupe_properties):
                return (
                    f"On ANT, but could not dupe check (could not extract {'/'.join(dupe_properties.keys())} from filename. "
                    f"{api_response[0].get('guid',self.guid_missing_message)}"
                )
            else:
                return self.perform_partial_dupe_check(dupe_properties, api_response)

        return self.perform_full_dupe_check()

    def check_if_films_can_be_uploaded(self, processed_films: pd.DataFrame):
        processed_films = processed_films.copy()
        processed_films["Already on ANT?"] = processed_films.apply(
            lambda film: self.check_if_film_is_duplicate(
                film["Full file path"],
                film["Resolution"],
                film["Codec"],
                film["Source"],
                film["API response"],
            ),
            axis=1,
        )

        return processed_films

    def check_if_film_is_duplicate(
        self,
        full_file_path: str,
        resolution: str,
        codec: str,
        source: str,
        api_response: list[dict[str, Any]],
    ) -> str:
        if not api_response:
            return self.not_found_value

        file_name = Path(full_file_path).name

        filename_info_if_match = self.check_if_filename_exists_on_ant(
            file_name, api_response
        )
        if filename_info_if_match is not None:
            return filename_info_if_match

        return self.check_remaining_dupe_properties(
            resolution, codec, source, api_response
        )

    def check_if_filename_exists_on_ant(
        self, file_name: str, api_response: list[dict[str, Any]]
    ) -> Union[str, None]:
        for existing_upload in api_response:
            uploaded_files = existing_upload.get("files", [])

            if uploaded_files:
                for file_info in uploaded_files:
                    if file_name == file_info.get("name", ""):
                        return f"Duplicate - exact filename already exists on ANT: {existing_upload.get('guid',self.guid_missing_message)}"

    def check_if_film_exists_on_ant(self, film_title: str) -> list[dict[str, Any]]:
        """
        Take a film title, and search for it using the ANT API.
        If an initial match is not found, re-search for a
        modified version of the film title if it meets certain conditions.
        """
        logging.info("\nSearching for %s...", film_title)
        title_checks = [
            (self.search_for_film_title_on_ant, ""),
            (self.search_for_film_if_contains_and, ""),
            (self.search_for_film_if_contains_potential_date_or_time, "time"),
            (self.search_for_film_if_contains_potential_date_or_time, "date"),
            (self.search_for_film_if_contains_aka, ""),
        ]
        for search_function, optional_argument in title_checks:
            try:
                if optional_argument:
                    search_result = search_function(film_title, optional_argument)
                else:
                    search_result = search_function(film_title)

                if search_result:
                    return search_result
            except Exception as err:
                logging.error(
                    "An unexpected error occured, skipping film:\n%s", str(err)
                )

        logging.info("--- Not found on ANT ---")
        return []

    def search_for_film_if_contains_and(self, film_title: str) -> list[dict[str, Any]]:
        """
        If film title contains and or &, replace with the oppposite
        and search for the new title on ANT. Else, return NOT FOUND.
        """
        and_word_regex = r"(?i)\sand\s"
        and_symbol_regex = r"(?i)\s&\s"

        if re.search(and_word_regex, film_title):
            logging.info("-- Film contains 'and'")
            return self.replace_word_and_re_search(film_title, and_word_regex, " & ")
        elif re.search(and_symbol_regex, film_title):
            logging.info("-- Film contains '&'")
            return self.replace_word_and_re_search(
                film_title, and_symbol_regex, " and "
            )

        return []

    def search_for_film_if_contains_potential_date_or_time(
        self, film_title: str, format: str
    ) -> list[dict[str, Any]]:
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

        return []

    def search_for_film_if_contains_aka(self, film_title: str) -> list[dict[str, Any]]:
        aka_regex = r"(?i)\saka\s"

        if re.search(aka_regex, film_title):
            logging.info("-- Film title may contain an alternate title")

            split_titles = re.split(aka_regex, film_title)

            for title in split_titles:
                logging.info("-- Searching for %s as well...", title)
                film_search = self.search_for_film_title_on_ant(title)
                if film_search is not None:
                    return film_search
        return []

    def replace_word_and_re_search(
        self, film_title: str, regex_pattern: str, replacement: str
    ) -> list[dict[str, Any]]:
        cleaned_film_title = re.sub(
            regex_pattern,
            replacement,
            film_title,
        )
        logging.info("-- Searching for %s as well...", cleaned_film_title)

        return self.search_for_film_title_on_ant(cleaned_film_title)

    @sleep_and_retry
    @limits(calls=1, period=2)
    def search_for_film_title_on_ant(self, film_title: str) -> list[dict[str, Any]]:
        """
        Use the ANT API to search for a film title and
        return the first URL if found, else a NOT FOUND string
        """

        if not self.api_key:
            logging.error(
                "The API key entered is blank, please re-run and enter a valid API key"
            )
            raise SystemExit("Exiting due to blank API key")

        payload = {
            "api_key": self.api_key,
            "q": film_title,
            "t": "movie",
            "o": "json",
        }

        response = self.session.get(self.ant_url, params=payload)
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

        if response_json["response"]["total"] > 0:
            return response_json["item"]
        else:
            return []
