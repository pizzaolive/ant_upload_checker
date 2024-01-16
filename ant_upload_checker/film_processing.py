import pandas as pd
import requests
import logging
import guessit
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from ant_upload_checker.parameters import API_KEY
from ant_upload_checker.parameters import INPUT_FOLDER


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


def get_clean_film_file_paths(input_folder):
    paths = get_film_file_paths(input_folder)

    cleaned_paths = remove_paths_containing_extras_folder(paths)

    paths_df = (
        pd.DataFrame({"full path": cleaned_paths})
        .sort_values(by="full path")
        .reset_index(drop=True)
    )

    return paths_df


def remove_paths_containing_extras_folder(paths):
    cleaned_paths = [path for path in paths if path.parent.name != "Extras"]

    return cleaned_paths


def get_film_details_from_path(paths_df):
    paths_with_info = add_stem_column(paths_df).pipe(add_film_name_column)

    return paths_with_info


def add_stem_column(paths_df):
    paths_with_stem = paths_df.copy()
    paths_with_stem["file name"] = paths_df["full path"].apply(lambda x: x.stem)

    return paths_with_stem


def add_film_name_column(paths_df):
    paths_with_file_name = paths_df.copy()
    paths_with_file_name["film name"] = (
        paths_with_file_name["file name"]
        .astype(str)
        .replace({r"\(|\)": ""}, regex=True)
        .pipe(replace_dots_between_word_boundaries)
        .pipe(replace_spaces_between_consecutive_single_letters_with_dots)
        .pipe(remove_edition_info)
        .str.extract(r"(.*?)(?=\s\d{4})")
    )
    return paths_with_file_name


def replace_dots_between_word_boundaries(file_name_series):
    cleaned_file_names = file_name_series.replace(
        {r"(?<=\b)\.(?=\b|\d)": " "}, regex=True
    )
    return cleaned_file_names


def replace_spaces_between_consecutive_single_letters_with_dots(file_name_series):
    cleaned_file_names = file_name_series.replace(
        {r"(?<=\b[A-z]{1})\s(?=[A-z]{1}\b)": "."}, regex=True
    )
    return cleaned_file_names


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
