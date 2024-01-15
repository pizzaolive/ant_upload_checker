import logging
from ant_upload_checker.film_processing import (
    get_video_file_paths,
    get_film_details_from_path,
    check_if_films_exist_on_anthelion,
)
from ant_upload_checker.parameters import INPUT_FOLDER
from ant_upload_checker.output import write_film_list_to_csv


def main():
    logging.basicConfig(level=logging.INFO)

    film_info = (
        get_video_file_paths(INPUT_FOLDER)
        .pipe(get_film_details_from_path, limit_to_5=False)
        .pipe(check_if_films_exist_on_anthelion)
    )

    write_film_list_to_csv(film_info)

    logging.info("Script has ended")


if __name__ == "__main__":
    main()
