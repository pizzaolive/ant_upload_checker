import requests
import logging
from pathlib import Path
from typing import Any, Union
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter, Retry
import pandas as pd
import rapidfuzz


class FilmSearcher:
    def __init__(
        self,
        film_list_df: pd.DataFrame,
        api_key_ant: str,
        api_key_tmdb: str,
        ant_url: str,
        tmdb_url: str,
    ):
        self.film_list_df: pd.DataFrame = film_list_df
        self.api_key_ant: str = api_key_ant
        self.api_key_tmdb: str = api_key_tmdb
        self.ant_url: str = ant_url
        self.tmdb_url: str = tmdb_url
        self.session: requests.Session = requests.Session()
        self.not_found_value: str = "NOT FOUND"

        retries = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def check_if_films_exist_on_ant(self) -> pd.DataFrame:
        """
        Given pandas DataFrame of film list, if list contains
        films that were on ANT and duplicates, then skip these films.
        For any not found, non-dupes, or new films in the list,
        search for these on ANT, indicating whether they exist on ANT or not.
        """
        regex_to_skip = r"^Duplicate|^Banned"

        self.film_list_df["Should skip"] = self.film_list_df[
            "Already on ANT?"
        ].str.contains(regex_to_skip, regex=True, na=False)

        films_to_skip = self.film_list_df.loc[self.film_list_df["Should skip"]]

        if not films_to_skip.empty:
            logging.info(
                "Skipping %s films already found on ANT in the previous output file...",
                len(films_to_skip),
            )
        else:
            logging.info(
                "No films were skipped as any existing film list did not contain duplicates."
            )

        films_to_process = (
            self.film_list_df.drop(films_to_skip.index)
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )

        films_to_process["TMDB ID"] = films_to_process.apply(
            lambda film: self.search_for_film_on_tmdb(
                film["Parsed film title"],
                film["Release year"],
            ),
            axis=1,
            result_type="expand",
        )

        films_to_process["API response"] = films_to_process["TMDB ID"].apply(
            self.check_if_film_exists_on_ant
        )

        films_to_dupe_check = (
            pd.concat([films_to_skip, films_to_process])
            .sort_values(by="Parsed film title")
            .reset_index(drop=True)
        )

        # Ensure NAs incl. those from old versions are converted to empty lists
        films_to_dupe_check["API response"] = (
            films_to_dupe_check["API response"].fillna("").apply(list)
        )

        return films_to_dupe_check

    def check_if_film_exists_on_ant(self, film_id: str) -> list[dict[str, Any]]:
        """
        Take a film title, and search for it using the ANT API.
        If an initial match is not found, re-search for a
        modified version of the film title if it meets certain conditions.
        """
        logging.info("\nSearching for %s...", film_id)
        title_checks = [
            self.search_for_film_on_ant,
        ]
        for search_function in title_checks:
            try:
                search_result = search_function(film_id)

                if search_result:
                    return search_result
            except Exception as err:
                logging.error(
                    "An unexpected error occured, skipping film:\n%s", str(err)
                )

        logging.info("--- Not found on ANT ---")
        return []

    @sleep_and_retry
    @limits(calls=1, period=0.25)
    def search_for_film_on_tmdb(self, film_title: str, release_year: str):
        if film_title == "":
            logging.info("No film title, skipping")
            return ""
        logging.info(film_title)
        # Avoid using release year in query due to bad metadata
        # or incorrect year in filenames
        payload = {
            "api_key": self.api_key_tmdb,
            "query": film_title,
            "include_adult": "false",
            "language": "en-us",
        }
        response_json = self.search_for_film_using_api(payload, url=self.tmdb_url)

        if not response_json["results"]:
            logging.info("Request to TMDB returned no results, skipping")
            return ""

        unmatched_films = []
        for film in response_json["results"]:
            response_release_year = film["release_date"][0:4]
            title_match = (film["title"] == film_title) | (
                film["original_title"] == film_title
            )
            year_match = response_release_year == release_year

            if title_match and year_match:
                logging.info(
                    "---- Exact title and year match to TMDB. ID: %s", film["id"]
                )
                return film["id"]
            corrected_year_match = (
                response_release_year == str(int(release_year) + 1)
            ) or (response_release_year == str(int(release_year) - 1))

            if title_match and corrected_year_match:
                info_message = (
                    f"---- Exact title match but TMDB release year ({response_release_year}) "
                    f"is one year later or before extracted from filename ({release_year}). ID: {film['id']}\n"
                    "---- This may be due to an earlier premier date but is worth double checking."
                )
                logging.info(info_message)
                return film["id"]

            if year_match or corrected_year_match:
                unmatched_films.append(film)

        all_film_titles = [film["title"] for film in unmatched_films]
        best_fuzzy_match = rapidfuzz.process.extractOne(film_title, all_film_titles)

        if best_fuzzy_match[1] > 85:
            fuzzy_matched_film = unmatched_films[best_fuzzy_match[2]]

            logging.info(
                "---- Warning: could not find exact film match, resorting to fuzzy matching. Manual check is recommended!\n"
                f"---- TMDB film name: '{fuzzy_matched_film['title']}'. TMDB ID: {fuzzy_matched_film['id']} "
            )
            return fuzzy_matched_film["id"]

        logging.info("Failed match film to TMDB, skipping")
        return ""

    @sleep_and_retry
    @limits(calls=1, period=2)
    def search_for_film_on_ant(self, film_id: str) -> list[dict[str, Any]]:
        payload = {
            "api_key": self.api_key_ant,
            "tmdb": film_id,
            "t": "movie",
            "o": "json",
        }
        response_json = self.search_for_film_using_api(payload, url=self.ant_url)

        if response_json["response"]["total"] > 0:
            return response_json["item"]
        else:
            return []

    def search_for_film_using_api(
        self, payload: dict[str, str], url: str
    ) -> dict[Any, Any]:
        response = self.session.get(url, params=payload)
        try:
            response.raise_for_status()

            # Handle tracker returning 200 when down
            if response.status_code == 200 and "maintenance" in response.text.lower():
                error_message = (
                    "Tracker appears to be down for maintenance: '%s'",
                    response.text,
                )
                logging.error(error_message)
                raise SystemExit(error_message)

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
        except Exception as err:
            logging.error("An unknown error occured: %s", err)
            raise SystemExit(err)

        return response_json
