import pandas as pd
import requests
import logging
from guessit import guessit
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from ant_upload_checker.parameters import API_KEY
from ant_upload_checker.parameters import INPUT_FOLDER
import re


def get_film_file_paths():
    file_extensions = ["mkv", "m2ts"]

    paths = []
    for ext in file_extensions:
        paths.extend(Path(INPUT_FOLDER).glob(f"**/*.{ext}"))

    if not paths:
        raise ValueError(
            "No films were found, check the INPUT_FOLDER value in parameters.py"
        )

    return paths


def get_titles_from_film_paths(film_paths):
    titles = [get_film_title_from_path(path) for path in film_paths]
    cleaned_titles = [fix_title_if_contains_acronym(title) for title in titles]

    return cleaned_titles


def get_film_title_from_path(path):
    film_title = guessit(path)["title"]

    return film_title


def fix_title_if_contains_acronym(film_title):
    """
    e.g. L A Confidential -> L.A Confidential -> L.A. Confidential
    """
    titles_with_acronym_spaces_as_dots = re.sub(
        r"(?<=\b[A-z]{1})\s(?=[A-z]{1}\b)", ".", film_title
    )

    title_with_acronym_suffixed_with_a_dot = re.sub(
        r"(?<=\.[A-z]{1})\s(?=[^\s])", ". ", titles_with_acronym_spaces_as_dots
    )

    return title_with_acronym_suffixed_with_a_dot


def remove_paths_containing_extras_folder(paths):
    cleaned_paths = [path for path in paths if path.parent.name != "Extras"]

    return cleaned_paths


def remove_edition_info(file_name_series):
    # Need tests for this
    cleaned_file_names = file_name_series.replace(
        {r"(?i)(theatrical|extended)\scut\s": ""}, regex=True
    )
    return cleaned_file_names


@sleep_and_retry
@limits(calls=1, period=2)
def check_if_film_exists_on_ant(film_name):
    logging.info("Searching for %s", film_name)
    url = "https://anthelion.me/api.php"

    if API_KEY == "":
        raise ValueError("The API_KEY must be set in parameters.py")

    json = {
        "api_key": API_KEY,
        "q": film_name,
        "t": "movie",
        "o": "json",
        "limit": 1,
    }
    response = requests.get(url, json).json()

    if response["response"]["total"] == 0:
        return "NOT FOUND"
    else:
        torrent_link = response["item"][0]["guid"]
        return torrent_link


def check_if_films_exist_on_ant(films_df):
    films_df_output = films_df.copy()
    films_df_output["already on ANT?"] = films_df_output["film name"].apply(
        check_if_film_exists_on_ant
    )

    return films_df_output
