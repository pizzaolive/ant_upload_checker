import logging
from ant_upload_checker.film_processing import (
    get_filtered_film_file_paths,
    get_formatted_titles_from_film_paths,
    create_film_list_dataframe,
    check_if_films_exist_on_ant,
)

from ant_upload_checker.output import write_film_list_to_csv


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S"
    )

    film_file_paths = get_filtered_film_file_paths()
    film_titles = get_formatted_titles_from_film_paths(film_file_paths)

    films_df = create_film_list_dataframe(film_file_paths, film_titles)
    films_checked_on_ant = check_if_films_exist_on_ant(films_df)

    write_film_list_to_csv(films_checked_on_ant)

    logging.info("Script has ended")


if __name__ == "__main__":
    main()
