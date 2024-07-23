import logging
from pathlib import Path
from ant_upload_checker.setup import (
    setup_logging,
    get_user_information,
    load_existing_env_file,
)
from ant_upload_checker.film_processor import FilmProcessor
from ant_upload_checker.film_searcher import FilmSearcher
from ant_upload_checker.output import write_film_list_to_csv
from ant_upload_checker.parameters import INPUT_FOLDERS, OUTPUT_FOLDER

import os


def main():
    setup_logging()
    logging.info("Starting ANT upload checker...")

    get_user_information()
    api_key, input_folders = load_existing_env_file()

    films = FilmProcessor(input_folders, OUTPUT_FOLDER)
    film_file_paths = films.get_film_file_paths()
    film_list_df = films.get_film_info_from_file_paths(film_file_paths)

    film_list_combined = films.combine_with_existing_film_csv(film_list_df)

    film_searcher = FilmSearcher(film_list_combined, api_key)
    films_checked_on_ant = film_searcher.check_if_films_exist_on_ant()

    write_film_list_to_csv(films_checked_on_ant)

    logging.info("\nScript has ended")


if __name__ == "__main__":
    main()
