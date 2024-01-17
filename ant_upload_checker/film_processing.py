import pandas as pd
import requests
import logging
from guessit import guessit
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from ant_upload_checker.parameters import API_KEY
from ant_upload_checker.parameters import INPUT_FOLDER
import re


def get_filtered_film_file_paths():
    film_paths = get_film_file_paths()
    filtered_film_paths = remove_paths_containing_extras_folder(film_paths)

    return filtered_film_paths


def get_film_file_paths():
    """
    Scan the input folder from parameters for the given file extensions,
    adding any files to a list.
    """
    file_extensions = ["mkv", "m2ts"]

    paths = []
    for ext in file_extensions:
        paths.extend(Path(INPUT_FOLDER).glob(f"**/*.{ext}"))

    if not paths:
        raise ValueError(
            "No films were found, check the INPUT_FOLDER value in parameters.py"
        )

    return paths


def remove_paths_containing_extras_folder(paths):
    """
    Remove any file paths containing Extras as their parent folder.
    """
    cleaned_paths = [path for path in paths if path.parent.name != "Extras"]

    return cleaned_paths


def get_titles_from_film_paths(film_paths):
    """
    Use guessit to get film titles, then fix titles missing
    full stops within acronyms
    """
    titles = [get_film_title_from_path(path) for path in film_paths]
    cleaned_titles = [fix_title_if_contains_acronym(title) for title in titles]

    return cleaned_titles


def get_film_title_from_path(path):
    """
    Use the guessit package to extract the film title from
    a given file path
    """
    film_title = guessit(path)["title"]

    return film_title


def fix_title_if_contains_acronym(film_title):
    """
    After guessit has extracted film title, fix instances where
    consecutive single letter words contain spaces instead of full stops.
    e.g. L A Confidential -> L.A Confidential -> L.A. Confidential
    e.g. S W A T -> S.W.A.T -> S.W.A.T.
    """
    acronym_spaces_as_full_stops = re.sub(
        r"(?<=\b[A-Za-z]{1})\s(?=[A-Za-z]{1}\b)", ".", film_title
    )

    acronym_suffixed_with_a_full_stop = re.sub(
        r"(?<=\.[A-Za-z])(\s|$)(?=[^\s])", ". ", acronym_spaces_as_full_stops
    )

    acronym_at_end_of_title_suffixed_with_full_stop = re.sub(
        r"(?<=\..$)",
        ".",
        acronym_suffixed_with_a_full_stop,
    )

    return acronym_at_end_of_title_suffixed_with_full_stop


def create_film_list_dataframe(film_file_paths, film_titles):
    """
    Combine the full file paths and film titles into a
    pandas DataFrame.
    """
    films_df = pd.DataFrame(
        {"Full file paths": film_file_paths, "Parsed film title": film_titles}
    ).astype(str)

    return films_df


def check_if_films_exist_on_ant(films_df):
    """
    Add a new column to the DataFrame, indicating whether
    each film already exists on ANT or not.
    """
    films_checked_on_ant = films_df.copy()
    films_checked_on_ant["Already on ANT?"] = films_checked_on_ant["Parsed film title"].apply(
        check_if_film_exists_on_ant
    )

    return films_checked_on_ant


@sleep_and_retry
@limits(calls=1, period=2)
def check_if_film_exists_on_ant(film_title):
    """
    Use the ANT API to search for a film title and
    return the first URL if found, else a NOT FOUND string
    """
    logging.info("Searching for %s...", film_title)
    url = "https://anthelion.me/api.php"

    if API_KEY == "":
        raise ValueError("The API_KEY must be set in parameters.py")

    json = {
        "api_key": API_KEY,
        "q": film_title,
        "t": "movie",
        "o": "json",
        "limit": 1,
    } 
    response = requests.get(url, json).json()

    if response["response"]["total"] == 0:
        logging.info("--- Not found on ANT ---\n")
        return "NOT FOUND"
    else:
        torrent_link = response["item"][0]["guid"]
        return torrent_link
