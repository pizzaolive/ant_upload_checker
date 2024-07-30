import logging
from ant_upload_checker import setup
from ant_upload_checker.film_processor import FilmProcessor
from ant_upload_checker.film_searcher import FilmSearcher
from ant_upload_checker.output import write_film_list_to_csv


def main():
    setup.setup_logging()
    logging.info("Starting ANT upload checker...")

    setup.save_user_info_to_env()
    api_key, input_folders, output_folder = setup.load_env_file()

    films = FilmProcessor(input_folders, output_folder)
    film_file_paths = films.get_film_file_paths()
    film_list_df = films.get_film_info_from_file_paths(film_file_paths)

    film_list_combined = films.combine_with_existing_film_csv(film_list_df)

    film_searcher = FilmSearcher(film_list_combined, api_key)
    films_checked_on_ant = film_searcher.check_if_films_exist_on_ant()

    write_film_list_to_csv(films_checked_on_ant, output_folder)

    logging.info("\nScript has ended")


if __name__ == "__main__":
    main()
