import pandas as pd
import requests
import logging
from ratelimit import limits, sleep_and_retry
from ant_upload_checker.parameters import API_KEY
from ant_upload_checker.parameters import INPUT_FOLDER
import re


class FilmSearcher:
    def __init__(self, film_list_df, api_key):
        self.film_list_df = film_list_df
        self.api_key = api_key

    def check_if_films_exist_on_ant(self):
        """
        Given pandas DataFrame of film list, if list contains
        films that already contain a torrentid from previous output file,
        then skip these films. For any not found, or new films in the list,
        search for these on ANT, indicating whether they exist on ANT or not.
        """
        films_to_skip = self.film_list_df.loc[
            self.film_list_df["Already on ANT?"].str.contains("torrentid", na=False)
        ]
        logging.info(
            "Skipping %s films already found on ANT in the previous output file...",
            len(films_to_skip),
        )

        films_to_process = self.film_list_df.drop(films_to_skip.index)
        films_to_process["Already on ANT?"] = films_to_process[
            "Parsed film title"
        ].apply(self.check_if_film_exists_on_ant)

        films_checked_on_ant = (
            pd.concat([films_to_skip, films_to_process])
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )

        return films_checked_on_ant

    def check_if_film_exists_on_ant(self, film_title):
        """
        Take a film title, and search for it using the ANT API.
        If an initial match is not found, re-search for a
        modified version of the film title if it meets certain conditions.
        """
        logging.info("Searching for %s...", film_title)
        first_check = self.search_for_film_title_on_ant(film_title)

        if first_check != "NOT FOUND":
            return first_check

        second_check = self.search_for_film_if_contains_and(film_title)
        if second_check == "NOT FOUND":
            logging.info("--- Not found on ANT ---\n")

        return second_check

    def search_for_film_if_contains_and(self, film_title):
        """
        If film title contains and or &, replace with the oppposite
        and search for the new title on ANT. Else, return NOT FOUND.
        """
        and_word_regex = r"(?i)\sand\s"
        and_symbol_regex = r"(?i)\s&\s"

        if re.search(and_word_regex, film_title):
            return self.replace_word_and_re_search(film_title, and_word_regex, " & ")
        elif re.search(and_symbol_regex, film_title):
            return self.replace_word_and_re_search(
                film_title, and_symbol_regex, " and "
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
            "limit": 1,
        }
        response = requests.get(url, payload).json()

        if response["response"]["total"] == 0:
            return "NOT FOUND"
        else:
            torrent_link = response["item"][0]["guid"]
            return torrent_link

    def replace_word_and_re_search(self, film_title, regex_pattern, replacement):
        cleaned_film_title = re.sub(
            regex_pattern,
            replacement,
            film_title,
        )
        logging.info("Searching for %s as well, just in case...", cleaned_film_title)
        film_check = self.search_for_film_title_on_ant(cleaned_film_title)

        return film_check
