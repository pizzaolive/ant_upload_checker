import logging
from ant_upload_checker.film_processor import FilmProcessor
from ant_upload_checker.film_searcher import FilmSearcher
from ant_upload_checker.output import write_film_list_to_csv
from ant_upload_checker.parameters import INPUT_FOLDER, API_KEY, OUTPUT_FOLDER


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S"
    )

    films = FilmProcessor(INPUT_FOLDER, OUTPUT_FOLDER)
    film_file_paths = films.get_filtered_film_file_paths()
    film_list_df = films.get_film_info_from_file_paths(film_file_paths)

    film_searcher = FilmSearcher(film_list_df, API_KEY)
    films_checked_on_ant = film_searcher.check_if_films_exist_on_ant()

    write_film_list_to_csv(films_checked_on_ant)

    logging.info("Script has ended")


if __name__ == "__main__":
    main()
