import pandas as pd
import numpy as np
from rebulk.match import MatchesDict
import logging
from guessit import guessit
from pathlib import Path
import re
import sys
import shutil
from typing import List, Dict


class FilmProcessor:
    def __init__(self, input_folders: List[str], output_folder: str):
        self.file_extensions: List[str] = ["mp4", "avi", "mkv", "mpeg", "m2ts"]
        self.input_folders: List[str] = input_folders
        self.output_folder: Path = Path(output_folder)
        self.film_list_df_types: Dict[str, str] = {
            "Full file path": "string",
            "Parsed film title": "string",
            "Film size (GB)": "float64",
            "Resolution": "string",
            "Codec": "string",
            "Source": "string",
            "Release group": "string",
            "Already on ANT?": "string",
        }
        self.csv_file_path: Path = self.output_folder / "Film list.csv"
        self.backup_csv_file_path: Path = (
            self.output_folder / "Film list old version backup.csv"
        )

    def get_film_file_paths(self) -> List[Path]:
        """
        Scan the input folder from parameters for the given file extensions,
        adding any files to a list.
        """
        paths = []
        for ext in self.file_extensions:
            for folder in self.input_folders:
                paths.extend(Path(folder).glob(f"**/*.{ext}"))

        filtered_paths = self.remove_paths_containing_extras_folder(paths)
        cleaned_paths = self.remove_paths_if_unopenable(filtered_paths)

        if not cleaned_paths:
            raise ValueError(
                "No films were found, check the INPUT_FOLDERS value in parameters.py"
            )

        cleaned_paths.sort()

        return cleaned_paths

    def get_film_info_from_file_paths(
        self, film_file_paths: List[Path]
    ) -> pd.DataFrame:
        film_sizes = self.get_film_sizes_from_file_paths(film_file_paths)

        guessed_films = self.get_guessit_info_from_film_paths(film_file_paths)

        film_titles = self.get_formatted_titles_from_guessed_films(guessed_films)
        film_resolutions = self.get_film_resolutions_from_guessed_films(guessed_films)
        film_codecs = self.get_codecs_from_guessed_films(guessed_films)
        film_sources = self.get_source_from_guessed_films(guessed_films)
        release_groups = self.get_release_groups_from_guessed_films(guessed_films)

        film_list_df = self.create_film_list_dataframe(
            film_file_paths,
            film_sizes,
            film_titles,
            film_resolutions,
            film_codecs,
            film_sources,
            release_groups,
        )

        return film_list_df

    def combine_with_existing_film_csv(
        self, film_list_df: pd.DataFrame
    ) -> pd.DataFrame:
        should_read_csv = self.check_if_existing_film_csv_exists()

        if not should_read_csv:
            return film_list_df

        existing_film_list = pd.read_csv(self.csv_file_path)

        should_combine_film_lists = self.check_if_existing_csv_is_compatible(
            existing_film_list
        )

        if should_combine_film_lists:
            combined_film_list = self.combine_current_film_list_with_existing_csv(
                existing_film_list, film_list_df
            )

            return combined_film_list

        return film_list_df

    def combine_current_film_list_with_existing_csv(
        self, existing_film_list: pd.DataFrame, current_film_list: pd.DataFrame
    ) -> pd.DataFrame:

        logging.info(
            "Combining existing output file with current list of films "
            "and dropping duplicate film titles..."
        )
        existing_film_list_formatted = existing_film_list.astype(
            self.film_list_df_types
        )

        combined_film_list = (
            pd.concat([current_film_list, existing_film_list_formatted])
            .drop_duplicates(subset=["Parsed film title"], keep="last")
            .reset_index(drop=True)
        )

        self.stop_process_if_all_films_already_in_existing_csv(combined_film_list)

        return combined_film_list

    def stop_process_if_all_films_already_in_existing_csv(
        self, combined_film_list_df: pd.DataFrame
    ) -> None:
        if all(
            combined_film_list_df["Already on ANT?"].str.contains("torrentid", na=False)
        ):
            logging.info(
                "All films have already been searched and found on ANT in the previous "
                "output file.\n\nEnding the process early.\n\n----"
            )
            sys.exit(0)

    def remove_paths_containing_extras_folder(
        self, file_paths: List[Path]
    ) -> List[Path]:
        """
        Remove any file file paths containing Extras as their parent folder.
        """
        cleaned_paths = [path for path in file_paths if path.parent.name != "Extras"]

        return cleaned_paths

    def get_film_sizes_from_file_paths(self, file_paths: List[Path]) -> List[float]:
        film_sizes = [self.get_file_size_from_path(path) for path in file_paths]

    def remove_paths_if_unopenable(self, paths):
        """
        If file does not exist or is not openable, remove from paths.
        Warn user if path exceeds 260 characters.
        """
        cleaned_paths = []
        for path in paths:
            if not path.is_file():
                file_name = path.stem
                warning_message = (
                    f"{file_name} could not be opened or does not exist, skipping."
                )
                if len(str(path)) > 260:
                    warning_message += " This may be caused by a file path exceeding 260 characters. Try shortening the folder or file name."
                logging.warning(warning_message)
            else:
                cleaned_paths.append(path)

        return cleaned_paths

    def get_film_sizes_from_film_paths(self, film_paths):
        film_sizes = [self.get_file_size_from_path(path) for path in film_paths]

        return film_sizes

    def get_file_size_from_path(self, file_path: Path) -> float:
        file_size_in_bytes = file_path.stat().st_size
        file_size = self.convert_bytes_to_gb(file_size_in_bytes)

        return file_size

    def convert_bytes_to_gb(self, num_in_bytes: int) -> float:
        """
        Convert bytes to correct unit of measurement as a string
        """
        num_in_gb = round((num_in_bytes / 1073741824), 2)

        return num_in_gb

    def get_guessit_info_from_film_paths(
        self, file_paths: List[Path]
    ) -> List[MatchesDict]:
        """
        Use guessit package to extract film information
        into ordered dictionary.
        """
        guessed_films = [guessit(path) for path in file_paths]

        return guessed_films

    def get_formatted_titles_from_guessed_films(
        self, guessed_films: List[MatchesDict]
    ) -> List[str]:
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

    def get_film_attribute_from_guessed_film(
        self, guessed_film: MatchesDict, attribute: str
    ) -> str:
        """
        Extract the given guessit attribute from a given guessit object.
        """
        try:
            film_attribute = guessed_film[attribute]
            if isinstance(film_attribute, list):
                film_attribute = ", ".join(film_attribute)
        except:
            film_attribute = ""

        return film_attribute

    def get_film_resolutions_from_guessed_films(
        self, guessed_films: List[MatchesDict]
    ) -> List[str]:
        film_resolutions = [
            self.get_film_attribute_from_guessed_film(film, "screen_size")
            for film in guessed_films
        ]

        return film_resolutions

    def get_codecs_from_guessed_films(
        self, guessed_films: List[MatchesDict]
    ) -> List[str]:
        film_codecs = [
            self.get_film_attribute_from_guessed_film(film, "video_codec")
            for film in guessed_films
        ]

        return film_codecs

    def get_source_from_guessed_films(
        self, guessed_films: List[MatchesDict]
    ) -> List[str]:
        film_sources = [
            self.get_film_attribute_from_guessed_film(film, "source")
            for film in guessed_films
        ]

        film_sources_cleaned = [
            re.sub("Ultra HD Blu-ray", "Blu-ray", source) for source in film_sources
        ]

        return film_sources_cleaned

    def get_release_groups_from_guessed_films(
        self, guessed_films: List[MatchesDict]
    ) -> List[str]:
        release_groups = [
            self.get_film_attribute_from_guessed_film(film, "release_group")
            for film in guessed_films
        ]

        return release_groups

    def fix_title_if_contains_acronym(self, film_title: str) -> str:
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
        film_file_paths: List[Path],
        film_sizes: List[float],
        film_titles: List[str],
        film_resolutions: List[str],
        film_codecs: List[str],
        film_sources: List[str],
        film_release_groups: List[str],
    ) -> pd.DataFrame:
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
                "Codec": film_codecs,
                "Source": film_sources,
                "Release group": film_release_groups,
                "Already on ANT?": np.repeat(pd.NA, len(film_file_paths)),
            }
        ).astype(self.film_list_df_types)

        return films_df

    def check_if_existing_film_csv_exists(self) -> bool:
        if not self.csv_file_path.is_file():
            logging.info(
                "An existing output file (%s) was not found, processing films "
                "from scratch...",
                self.csv_file_path,
            )
            return False

        logging.info("An existing output file (%s) was found.", self.csv_file_path)

        return True

    def check_if_existing_csv_is_compatible(
        self, existing_film_df: pd.DataFrame
    ) -> bool:
        existing_columns = list(existing_film_df.columns)

        if existing_columns != list(self.film_list_df_types.keys()):
            logging.warning(
                "Warning: existing file was created using an old version of ANT upload checker.\n"
                "-------- Existing file is being skipped as it doesn't contain all the required columns.\n"
                "-------- Creating a backup film list from the previous version (%s).\n"
                "-------- This can be deleted if you don't need it.\n",
                self.backup_csv_file_path,
            )

            shutil.copy(self.csv_file_path, self.backup_csv_file_path)

            return False

        return True
