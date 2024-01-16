import logging
from ant_upload_checker.film_processing import (
    get_film_file_paths,
    remove_paths_containing_extras_folder,
    get_titles_from_film_paths
)

from ant_upload_checker.output import write_film_list_to_csv


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S"
    )

    paths = get_film_file_paths()
    filtered_paths = remove_paths_containing_extras_folder(paths)
    film_titles = get_titles_from_film_paths(filtered_paths)


    write_film_list_to_csv(film_info)

    logging.info("Script has ended")


if __name__ == "__main__":
    main()
