import requests
import logging
import re
from typing import Any, Optional
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter, Retry
import pandas as pd
import rapidfuzz


class FilmSearcher:
    def __init__(
        self,
        films_df: pd.DataFrame,
        api_key_ant: str,
        api_key_tmdb: str,
        ant_url: str,
        tmdb_url: str,
    ):
        self.films_df: pd.DataFrame = films_df
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
        If films DataFrame contains films that were on ANT and duplicates, then skip these.
        For any not found, non-dupes, or new films,
        search for these on TMDB, then ANT, indicating whether they exist on ANT or not.
        """
        regex_to_skip = r"^Duplicate|^Banned"

        self.films_df["Should skip"] = self.films_df["Already on ANT?"].str.contains(
            regex_to_skip, regex=True, na=False
        )

        films_to_skip = self.films_df.loc[self.films_df["Should skip"]]

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
            self.films_df.drop(films_to_skip.index)
            .sort_values(by="title")
            .reset_index(drop=True)
        )

        films_dict = films_to_process.to_dict(orient="records")
        for film in films_dict:
            film["TMDB ID"] = self.search_for_film_on_tmdb(
                film["title"], film["year"], film["runtime"], film["edition"]
            )
        for film in films_dict:
            film["API response"] = self.check_if_film_exists_on_ant(
                film["TMDB ID"], film["title"]
            )

        processed_films = pd.DataFrame(films_dict)

        films_to_dupe_check = (
            pd.concat([films_to_skip, processed_films])
            .sort_values(by="title")
            .reset_index(drop=True)
        )

        # Ensure NAs incl. those from old versions are converted to empty lists
        films_to_dupe_check["API response"] = (
            films_to_dupe_check["API response"].fillna("").apply(list)
        )

        return films_to_dupe_check

    def check_if_film_exists_on_ant(
        self, tmdb_id: str, film_title: str
    ) -> list[Optional[dict[str, Any]]]:
        """
        Take a film title, and search for it using the ANT API.
        If an initial match is not found, re-search for a
        modified version of the film title if it meets certain conditions.
        """
        logging.info("\nSearching for %s...", film_title)

        if not tmdb_id:
            logging.info("--- Could not match film to TMDB, skipping ANT search.")
            return []

        try:
            # TODO add in film title to fall back on title search if no TMDB ID could be found
            search_result = self.search_for_film_on_ant(tmdb_id)
            if search_result:
                return search_result
        except Exception as err:
            logging.error("An unexpected error occured, skipping film:\n%s", str(err))

        logging.info(f"--- TMDB {tmdb_id} Not found on ANT ---")
        return []

    def validate_tmdb_match(
        self, film: dict[str, Any], runtime: int, edition: str
    ) -> bool:
        payload = {
            "api_key": self.api_key_tmdb,
        }
        movie_details_url = f"https://api.themoviedb.org/3/movie/{film['id']}"
        response_json = self.search_for_film_using_api(payload, movie_details_url)

        tmdb_runtime = response_json.get("runtime", None)
        if tmdb_runtime is not None:
            runtime_difference = abs(runtime - tmdb_runtime)
            if runtime_difference < 10:
                return True
            elif edition and edition != "theatrical":
                logging.info(
                    "---- Edition is: %s. Not using runtime to verify", edition
                )
                return True
            else:
                logging.info("---- Runtime does not match")
                return False

        logging.info("No TMDB ID available, unable to verify")

    def normalise_title(self, title: str) -> str:
        normalised_title = re.sub(r"[^\w\s]", "", title).lower()
        return normalised_title

    @sleep_and_retry
    @limits(calls=1, period=0.25)
    def search_for_film_on_tmdb(
        self, film_title: str, release_year: int, runtime: int, edition: str
    ):
        if film_title == "":
            logging.info("No film title, skipping")
            return ""

        logging.info(f"Searching for {film_title} on TMDB")

        payload = {
            "api_key": self.api_key_tmdb,
            "query": film_title,
            "include_adult": "false",
            "language": "en-us",
        }

        if release_year:
            payload["primary_release_year"] = str(release_year)

        response_json = self.search_for_film_using_api(payload, url=self.tmdb_url)

        unmatched_films = []
        if response_json["results"]:
            year_match = True if release_year else False

            for film in response_json["results"]:
                title_match = self.normalise_title(
                    film["title"]
                ) == self.normalise_title(film_title)

                if title_match and year_match:
                    logging.info("---- Title and year match")
                    if self.validate_tmdb_match(film, runtime, edition):
                        logging.info(
                            "---- TMDB ID: %s",
                            film["id"],
                        )
                        return film["id"]
                else:
                    unmatched_films.append(film)

        # expand API search this time, then fuzzy match
        if release_year:
            expanded_release_years = [release_year + 1, release_year - 1]

            for year in expanded_release_years:
                payload["primary_release_year"] = year
                response_json = self.search_for_film_using_api(
                    payload, url=self.tmdb_url
                )
                if response_json["results"]:
                    unmatched_films += response_json["results"]

            if unmatched_films:
                unmatched_films_by_popularity = sorted(
                    unmatched_films, key=lambda x: x["popularity"], reverse=True
                )

                all_film_titles = [
                    film["title"] for film in unmatched_films_by_popularity
                ]
                fuzzy_match_scores = rapidfuzz.process.extract(
                    film_title, all_film_titles, scorer=rapidfuzz.fuzz.token_sort_ratio
                )

                for fuzzy_match_score in fuzzy_match_scores:
                    index = fuzzy_match_score[2]
                    fuzzy_matched_film = unmatched_films_by_popularity[index]

                    if self.validate_tmdb_match(fuzzy_matched_film, runtime, edition):
                        logging.info(
                            "---- Warning: could not find exact film match, expanded release year and using "
                            "fuzzy matching. Manual check is recommended!\n"
                            f"---- Parsed film info: {film_title} ({release_year})\n"
                            f"---- TMDB film name:   {fuzzy_matched_film['title']} ({fuzzy_matched_film["release_date"][0:4]}).\n"
                            f"---- TMDB ID: {fuzzy_matched_film['id']}"
                        )
                        return fuzzy_matched_film["id"]

        logging.info("Failed to match film")
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
