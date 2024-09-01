from typing import Any, Union
from pathlib import Path
import pandas as pd
from ant_upload_checker import constants


class DupeChecker:
    def __init__(self, films_to_dupe_check: pd.DataFrame):
        self.films_to_dupe_check: pd.DataFrame = films_to_dupe_check
        self.guid_missing_message: str = "(Failed to extract URL from API response)"
        self.not_found_value: str = "NOT FOUND"
        self.banned_groups = constants.BANNED_GROUPS

    def check_if_films_can_be_uploaded(self) -> pd.DataFrame:
        dupe_checked_films = self.films_to_dupe_check.copy()

        films_to_skip = dupe_checked_films.loc[dupe_checked_films["Should skip"]]
        films_to_dupe_check = dupe_checked_films.loc[
            ~dupe_checked_films["Should skip"]
        ].copy()

        films_to_dupe_check["Already on ANT?"] = films_to_dupe_check.apply(
            lambda film: self.check_if_film_is_duplicate(
                film["Full file path"],
                film["Resolution"],
                film["Codec"],
                film["Source"],
                film["Release group"],
                film["API response"],
            ),
            axis=1,
        )

        combined_films = (
            pd.concat([films_to_skip, films_to_dupe_check])
            .sort_index()
            .drop(["Should skip", "API response"], axis=1)
        )

        return combined_films

    def check_if_film_is_duplicate(
        self,
        full_file_path: str,
        resolution: str,
        codec: str,
        source: str,
        release_group: str,
        api_response: list[dict[str, Any]],
    ) -> str:
        if not api_response:
            return self.not_found_value

        # Retain lower() to account for previous film list versions
        if release_group.lower() in self.banned_groups:
            return f"Release group '{release_group}' is banned from ANT - do not upload"

        file_name = Path(full_file_path).name

        filename_info_if_match = self.check_if_filename_exists_on_ant(
            file_name, api_response
        )
        if filename_info_if_match is not None:
            return filename_info_if_match

        dupe_properties = {"resolution": resolution, "codec": codec, "media": source}
        return self.check_remaining_dupe_properties(dupe_properties, api_response)

    def check_if_filename_exists_on_ant(
        self, file_name: str, api_response: list[dict[str, Any]]
    ) -> Union[str, None]:
        for existing_upload in api_response:
            uploaded_files = existing_upload.get("files", [])

            if uploaded_files:
                for file_info in uploaded_files:
                    if file_name == file_info.get("name", ""):
                        return f"Duplicate: exact filename already exists: {existing_upload.get('guid',self.guid_missing_message)}"

    def check_remaining_dupe_properties(
        self,
        dupe_properties,
        api_response: list[dict[str, Any]],
    ) -> str:
        missing_properties = [k for k, v in dupe_properties.items() if not v]
        available_properties = {k: v for k, v in dupe_properties.items() if v}

        if len(missing_properties) == len(dupe_properties):
            return (
                f"On ANT, but could not dupe check (could not extract {'/'.join(missing_properties)} from filename). "
                f"{api_response[0].get('guid',self.guid_missing_message)}"
            )

        return self.perform_dupe_check(
            available_properties, missing_properties, api_response
        )

    def perform_dupe_check(
        self,
        available_properties: dict[str, str],
        missing_properties: list[str],
        api_response: list[dict[str, Any]],
    ) -> str:
        """
        With the available properties, check if the film is a full duplicate, partial duplicate,
        or not a duplicate.
        """

        available_properties_str = "/".join(available_properties.values())
        existing_guid = self.guid_missing_message

        for existing_upload in api_response:
            existing_guid = existing_upload.get("guid", self.guid_missing_message)

            is_duplicate = all(
                available_properties[prop].lower()
                == existing_upload.get(prop, "").lower()
                for prop in available_properties
            )
            if is_duplicate:
                dupe_string = f"a film with {available_properties_str} already exists"
                if missing_properties:
                    return (
                        f"Partial duplicate: {dupe_string}. Could not extract and check "
                        f"{'/'.join(missing_properties)} from filename. {existing_guid}"
                    )
                else:
                    return f"Duplicate: {dupe_string}: {existing_guid}"

        return f"Not a duplicate: a film with {available_properties_str} does not already exist. {existing_guid}"
