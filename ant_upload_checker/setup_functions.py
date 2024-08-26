import logging
import inquirer
from pathlib import Path
from dotenv import set_key, dotenv_values
from typing import List, Tuple
from ant_upload_checker.directory_selector import DirectorySelector


ENV_FILE_PATH = Path(".env").resolve()


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def check_if_user_wants_to_override_env_file() -> bool:
    question = [
        inquirer.List(
            "choice",
            message="Existing user settings were found, do you want to overwrite this?",
            choices=["Yes", "No"],
            default="No",
        )
    ]
    response = inquirer.prompt(question)

    return response["choice"] == "Yes"


def save_user_info_to_env() -> None:
    if not ENV_FILE_PATH.is_file() or check_if_user_wants_to_override_env_file():
        get_user_info_api_key()
        get_user_info_directories()
        logging.info("User setting saved to '.env' file")


def get_user_info_directories():
    selector = DirectorySelector()
    input_folders, output_folder = selector.run_directory_selector()
    input_directories_str = ",".join(input_folders)

    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="INPUT_FOLDERS",
        value_to_set=input_directories_str,
    )
    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="OUTPUT_FOLDER",
        value_to_set=output_folder,
    )


def get_user_info_api_key() -> None:
    prompt = [inquirer.Text("api_key", message="Please enter your API key from ANT")]

    user_api_key = inquirer.prompt(prompt)["api_key"]

    if user_api_key:
        set_key(
            dotenv_path=ENV_FILE_PATH,
            key_to_set="API_KEY",
            value_to_set=user_api_key,
        )
    else:
        raise ValueError("No API key was set - please restart")


def load_env_file() -> Tuple[str, list[Path], Path]:
    settings = dotenv_values(ENV_FILE_PATH)

    expected_settings = ["API_KEY", "INPUT_FOLDERS", "OUTPUT_FOLDER"]
    missing_settings = [
        setting for setting in expected_settings if settings.get(setting) is None
    ]

    if missing_settings:
        raise ValueError(
            f"The following user settings were not found in the '.env' file: {','.join(missing_settings)}"
            "\nPlease restart"
        )

    api_key = settings["API_KEY"]

    input_folders_str = settings["INPUT_FOLDERS"].split(",")
    input_folders = [Path(folder) for folder in input_folders_str]

    output_folder = Path(settings["OUTPUT_FOLDER"])

    logging.info("User settings loaded from '.env' file\n")

    return api_key, input_folders, output_folder
