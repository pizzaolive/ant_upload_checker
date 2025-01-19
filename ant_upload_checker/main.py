import logging
from ant_upload_checker import setup_functions
from ant_upload_checker import constants
from ant_upload_checker.film_processor import FilmProcessor
from ant_upload_checker.film_searcher import FilmSearcher
from ant_upload_checker.output import write_film_list_to_csv
from ant_upload_checker.dupe_checker import DupeChecker


def main():
    setup_functions.setup_logging()
    logging.info("Starting ANT upload checker...")

    setup_functions.save_user_info_to_env()
    api_key_ant, api_key_tmdb, input_folders, output_folder = (
        setup_functions.load_env_file()
    )

    films = FilmProcessor(input_folders, output_folder)
    films_df = films.get_film_info_from_file_paths()

    films_combined_df = films.combine_with_existing_film_csv(films_df)

    film_searcher = FilmSearcher(
        films_combined_df,
        api_key_ant=api_key_ant,
        api_key_tmdb=api_key_tmdb,
        ant_url=constants.ANT_URL,
        tmdb_url=constants.TMDB_URL,
    )
    films_to_dupe_check = film_searcher.check_if_films_exist_on_ant()

    dupe_checker = DupeChecker(films_to_dupe_check)
    films_checked_on_ant = dupe_checker.check_if_films_can_be_uploaded()

    write_film_list_to_csv(films_checked_on_ant, output_folder)

    logging.info("\nScript has ended")


if __name__ == "__main__":
    main()
