import logging
import re
import sys
import shutil
from pathlib import Path

import pandas as pd
import numpy as np
from rebulk.match import MatchesDict

from guessit import guessit

from ant_upload_checker.media_info_extractor import MediaInfoExtractor


class FilmProcessor:
    def __init__(self, input_folders: list[str], output_folder: str):
        self.file_extensions: list[str] = ["mp4", "avi", "mkv", "mpeg", "m2ts"]
        self.input_folders: list[str] = input_folders
        self.output_folder: Path = Path(output_folder)
        self.films_df_dtypes: dict[str, str] = {
            "title": "string",
            "year": "int64",
            "edition": "string",
            "source": "string",
            "release_group": "string",
            "file_path": "string",
            "runtime": "int64",
            "file_size": "float64",
            "resolution": "string",
            "codec": "string",
            "Already on ANT?": "string",
            "Info": "string",
        }
        self.csv_file_path: Path = self.output_folder / "Film list.csv"
        self.backup_csv_file_path: Path = (
            self.output_folder / "Film list old version backup.csv"
        )

    def get_film_file_paths(self) -> list[Path]:
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
        self, film_file_paths: list[Path]
    ) -> pd.DataFrame:

        media_info_extractor = MediaInfoExtractor(film_file_paths)
        metadata = media_info_extractor.extract_metadata_from_media_info()
        guessed_films = self.get_guessit_info_from_film_paths(film_file_paths)

        films_df = self.create_films_dataframe(
            film_file_paths, metadata, guessed_films
        ).pipe(self.clean_films_df)

        return films_df

    def clean_films_df(self, films_df: pd.DataFrame) -> pd.DataFrame:
        films_cleaned = films_df.replace({"source": {"Ultra HD Blu-ray": "Blu-ray"}})

        films_cleaned["release_group"] = films_cleaned["release_group"].str.lower()

        return films_cleaned

    def combine_with_existing_film_csv(self, films_df: pd.DataFrame) -> pd.DataFrame:
        should_read_csv = self.check_if_existing_film_csv_exists()

        if not should_read_csv:
            return films_df

        existing_film_list = pd.read_csv(self.csv_file_path)

        should_combine_film_lists = self.check_if_existing_csv_is_compatible(
            existing_film_list
        )

        if should_combine_film_lists:
            combined_film_list = self.combine_current_film_list_with_existing_csv(
                existing_film_list, films_df
            )

            return combined_film_list

        return films_df

    def combine_current_film_list_with_existing_csv(
        self, existing_film_list: pd.DataFrame, current_film_list: pd.DataFrame
    ) -> pd.DataFrame:

        logging.info(
            "Combining existing output file with current list of films "
            "and dropping duplicate film titles..."
        )
        existing_film_list_formatted = existing_film_list.astype(self.films_df_types)

        combined_film_list = (
            pd.concat([current_film_list, existing_film_list_formatted])
            .drop_duplicates(subset=["Parsed film title"], keep="last")
            .reset_index(drop=True)
            .fillna("")  # Fill NAs with empty strings for later dupe handling
        )

        self.stop_process_if_all_films_already_in_existing_csv(combined_film_list)

        return combined_film_list

    def stop_process_if_all_films_already_in_existing_csv(
        self, combined_films_df: pd.DataFrame
    ) -> None:
        if all(
            combined_films_df["Already on ANT?"].str.contains(
                r"^Duplicate:", regex=True, na=False
            )
        ):
            logging.info(
                "All films have already been searched and are duplicates. "
                "\n\nEnding the process early.\n\n----"
            )
            sys.exit(0)

    def remove_paths_containing_extras_folder(
        self, file_paths: list[Path]
    ) -> list[Path]:
        """
        Remove any file file paths containing Extras as their parent folder.
        """
        cleaned_paths = [path for path in file_paths if path.parent.name != "Extras"]

        return cleaned_paths

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

    def preprocess_file_name(self, file_name: str) -> str:
        cleaned_title = re.split(r"\bAKA\b", file_name, flags=re.IGNORECASE)[-1]
        # cleaned_title = re.sub("-", " ", cleaned_title)

        return cleaned_title

    def get_guessit_info_from_film_paths(
        self, file_paths: list[Path]
    ) -> list[MatchesDict]:
        """
        Use guessit package to extract film information
        into ordered dictionary.
        """
        cleaned_file_names = [
            self.preprocess_file_name(path.stem) for path in file_paths
        ]
        guessed_films = [guessit(file_name) for file_name in cleaned_file_names]

        return guessed_films

    def create_films_dataframe(
        self, film_file_paths, metadata, guessed_films
    ) -> pd.DataFrame:
        """
        Combine the full file paths and film titles into a
        pandas DataFrame.
        Add empty ANT check column before we attempt to combine an existing
        film list csv, in case one does not exist.
        """
        metadata_df = pd.DataFrame(metadata)
        metadata_df.insert(0, "file_path", film_file_paths)
        guessit_df = pd.DataFrame(guessed_films)

        films_df = (
            pd.concat([metadata_df, guessit_df], axis=1)
            .assign(**{"Already on ANT?": "", "Info": ""})
            .pipe(self.drop_non_film_files)
        )

        films_df = films_df[self.films_df_dtypes.keys()].astype(self.films_df_dtypes)

        return films_df

    def drop_non_film_files(self, films_df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove any files that guessit did not parse as 'movie', and log the removed
        file paths to the user.
        """
        filtered_df = films_df.copy()

        non_film_files = filtered_df.loc[filtered_df["type"] != "movie"]
        if not non_film_files.empty:
            logging.info(
                "Dropping the following titles as they have not been parsed as films:\n%s",
                non_film_files["title"].values,
            )
            filtered_df = filtered_df.drop(non_film_files.index).reset_index(drop=True)

        return filtered_df

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

        if existing_columns != list(self.films_df_dtypes.keys()):
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
