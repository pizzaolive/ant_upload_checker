import logging
from ant_upload_checker import setup_functions
from ant_upload_checker.film_processor import FilmProcessor
from ant_upload_checker.film_searcher import FilmSearcher
from ant_upload_checker.output import write_film_list_to_csv
from ant_upload_checker.dupe_checker import DupeChecker


def main():
    setup_functions.setup_logging()
    logging.info("Starting ANT upload checker...")

    setup_functions.save_user_info_to_env()
    api_key, input_folders, output_folder = setup_functions.load_env_file()

    films = FilmProcessor(input_folders, output_folder)
    film_file_paths = films.get_film_file_paths()
    film_list_df = films.get_film_info_from_file_paths(film_file_paths)

    film_list_combined = films.combine_with_existing_film_csv(film_list_df)

    film_searcher = FilmSearcher(film_list_combined, api_key)
    films_to_dupe_check = film_searcher.check_if_films_exist_on_ant()

    dupe_checker = DupeChecker(films_to_dupe_check)
    films_checked_on_ant = dupe_checker.check_if_films_can_be_uploaded()

    write_film_list_to_csv(films_checked_on_ant, output_folder)

    logging.info("\nScript has ended")


if __name__ == "__main__":
    main()
