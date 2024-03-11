import pandas as pd
import numpy as np
import logging
from guessit import guessit
from pathlib import Path
import re
from ant_upload_checker.parameters import INPUT_FOLDERS
import sys
import shutil


class FilmProcessor:
    def __init__(self, input_folders, output_folder):
        self.input_folders = input_folders
        self.output_folder = output_folder
        self.film_list_df_types = {
            "Full file path": str,
            "Film size (GB)": float,
            "Parsed film title": str,
            "Resolution": str,
            "Release group": str,
        }

    def get_filtered_film_file_paths(self):
        film_paths = self.get_film_file_paths()
        filtered_film_paths = self.remove_paths_containing_extras_folder(film_paths)

        return filtered_film_paths

    def get_film_info_from_file_paths(self, film_file_paths):
        film_sizes = self.get_film_sizes_from_film_paths(film_file_paths)

        guessed_films = self.get_guessit_info_from_film_paths(film_file_paths)
        film_titles = self.get_formatted_titles_from_guessed_films(guessed_films)
        film_resolutions = self.get_film_resolutions_from_guessed_films(guessed_films)
        release_groups = self.get_release_groups_from_guessed_films(guessed_films)

        film_list_df = self.create_film_list_dataframe(
            film_file_paths,
            film_sizes,
            film_titles,
            film_resolutions,
            release_groups,
        )

        return film_list_df

    def combine_with_existing_film_csv(self, film_list_df):
        existing_film_list_df = self.get_existing_film_list_if_exists()

        if isinstance(existing_film_list_df, pd.DataFrame):
            logging.info(
                "Combining existing output file with current list of films "
                "and dropping duplicate film titles..."
            )

            combined_film_list = (
                pd.concat([film_list_df, existing_film_list_df])
                .drop_duplicates(subset=["Parsed film title"], keep="last")
                .reset_index(drop=True)
            )

            self.stop_process_if_all_films_already_in_existing_csv(combined_film_list)

            return combined_film_list

        return film_list_df

    def stop_process_if_all_films_already_in_existing_csv(self, combined_film_list_df):
        if all(combined_film_list_df["Already on ANT?"].str.contains("torrentid")):
            logging.info(
                "All films have already been searched and found on ANT in the previous "
                "output file.\n\nEnding the process early.\n\n----"
            )
            sys.exit(0)

    def get_film_file_paths(self):
        """
        Scan the input folder from parameters for the given file extensions,
        adding any files to a list.
        """
        file_extensions = ["mp4", "avi", "mkv", "mpeg", "m2ts"]

        paths = []
        for ext in file_extensions:
            for folder in self.input_folders:
                paths.extend(Path(folder).glob(f"**/*.{ext}"))

        if not paths:
            raise ValueError(
                "No films were found, check the INPUT_FOLDERS value in parameters.py"
            )

        paths.sort()

        return paths

    def remove_paths_containing_extras_folder(self, paths):
        """
        Remove any file paths containing Extras as their parent folder.
        """
        cleaned_paths = [path for path in paths if path.parent.name != "Extras"]

        return cleaned_paths

    def get_film_sizes_from_film_paths(self, film_paths):
        film_sizes = [self.get_file_size_from_path(path) for path in film_paths]

        return film_sizes

    def get_file_size_from_path(self, path):
        file_size_in_bytes = path.stat().st_size
        file_size = self.convert_bytes_to_gb(file_size_in_bytes)

        return file_size

    def convert_bytes_to_gb(self, num_in_bytes):
        """
        Convert bytes to correct unit of measurement as a string
        """
        num_in_gb = round((num_in_bytes / 1073741824), 2)

        return num_in_gb

    def get_guessit_info_from_film_paths(self, film_paths):
        """
        Use guessit package to extract film information
        into ordered dictionary.
        """
        guessed_films = [guessit(path) for path in film_paths]

        return guessed_films

    def get_formatted_titles_from_guessed_films(self, guessed_films):
        """
        Get film titles from guessit objects, then fix titles missing
        full stops within acronyms
        """
        titles = [
            self.get_film_attribute_from_guessed_film(film, "title")
            for film in guessed_films
        ]
        cleaned_titles = [self.fix_title_if_contains_acronym(title) for title in titles]

        return cleaned_titles

    def get_film_attribute_from_guessed_film(self, guessed_film, attribute):
        """
        Extract the given guessit attribute from a given guessit object.
        """
        try:
            film_attribute = guessed_film[attribute]
        except:
            film_attribute = ""

        return film_attribute

    def get_film_resolutions_from_guessed_films(self, guessed_films):
        film_resolutions = [
            self.get_film_attribute_from_guessed_film(film, "screen_size")
            for film in guessed_films
        ]

        return film_resolutions

    def get_release_groups_from_guessed_films(self, guessed_films):
        release_groups = [
            self.get_film_attribute_from_guessed_film(film, "release_group")
            for film in guessed_films
        ]

        return release_groups

    def fix_title_if_contains_acronym(self, film_title):
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

    def create_film_list_dataframe(
        self,
        film_file_paths,
        film_sizes,
        film_titles,
        film_resolutions,
        film_release_groups,
    ):
        """
        Combine the full file paths and film titles into a
        pandas DataFrame.
        Add empty ANT check column before we attempt to combine an existing
        film list csv, in case one does not exist.
        """
        films_df = pd.DataFrame(
            {
                "Full file path": film_file_paths,
                "Parsed film title": film_titles,
                "Film size (GB)": film_sizes,
                "Resolution": film_resolutions,
                "Release group": film_release_groups,
                "Already on ANT?": np.repeat(np.nan, len(film_file_paths)),
            }
        ).astype(self.film_list_df_types)

        return films_df

    def get_existing_film_list_if_exists(self):
        output_file_path = Path(self.output_folder).joinpath("Film list.csv")
        if not output_file_path.is_file():
            logging.info(
                "An existing output file at %s was not found, processing films "
                "from scratch...",
                output_file_path,
            )
            return None

        logging.info("An existing output file '%s' was found.", output_file_path)
        existing_film_list = pd.read_csv(output_file_path)

        existing_columns = existing_film_list.columns
        if (
            "Resolution" not in existing_columns
            or "Release group" not in existing_columns
        ):
            backup_path = Path(self.output_folder).joinpath(
                "Film list old version backup.csv"
            )
            logging.warning(
                "Warning: existing file was created using an old version of ANT upload checker.\n"
                "-------- Existing file is being skipped as it doesn't contain resolution info.\n"
                "-------- Creating a backup film list from the previous version (%s).\n"
                "-------- This can be deleted if you don't need it.\n",
                backup_path,
            )

            shutil.copy(output_file_path, backup_path)

            return None

        existing_film_list = existing_film_list.astype(self.film_list_df_types)

        return existing_film_list
