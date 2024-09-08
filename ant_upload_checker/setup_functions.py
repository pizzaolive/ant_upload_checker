import logging
import inquirer
from pathlib import Path
from dotenv import set_key, dotenv_values
from typing import Optional


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


def get_user_info_directories() -> None:
    output_folder = get_user_output_folder()
    input_folders = get_user_input_folders()

    input_folders_str = ",".join(input_folders)

    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="INPUT_FOLDERS",
        value_to_set=input_folders_str,
    )
    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="OUTPUT_FOLDER",
        value_to_set=output_folder,
    )


def prompt_user_for_info(
    info_required: str,
    prompt_message: str,
    logging_message: Optional[str] = None,
) -> str:

    if logging_message:
        logging.info(logging_message)

    prompt = [inquirer.Text(info_required, message=prompt_message)]
    response = inquirer.prompt(prompt)[info_required]

    return response


def get_user_output_folder() -> str:
    """
    Ask user for output folder, validate it can be converted to a Path object
    and it exists, then return as a string
    """
    logging_message = (
        "\n\nPlease enter the output folder (where the film list CSV should be saved)\n"
        "e.g. C:/Media or /home/username/media\n"
    )
    prompt_message = "Output folder"

    response = prompt_user_for_info("output_folder", prompt_message, logging_message)
    output_folder_path = return_as_path_if_valid(response)

    return str(output_folder_path)


def get_user_input_folders() -> list[str]:
    """
    Ask user for one or more input volders, validate they can be converted to Path objects
    and they exist, then return as list of strings
    """
    logging_message = (
        "\n\nPlease enter one or more input folders that contain your films.\n"
        "Multiple folders should be separated with a comma e.g. C:/Films,E:/Films\n"
    )
    prompt_message = "Input folder(s)"

    response = prompt_user_for_info("input_folders", prompt_message, logging_message)

    input_folders = response.split(",")

    valid_input_folder_paths = [
        return_as_path_if_valid(folder) for folder in input_folders
    ]

    valid_input_folders_str = [str(folder) for folder in valid_input_folder_paths]

    return valid_input_folders_str


def return_as_path_if_valid(folder_path_str: Optional[str]) -> Path:
    if not folder_path_str:
        raise ValueError("No folder path was selected in the dialog box, please re-run")

    folder_path_str_formatted = folder_path_str.lstrip()
    folder_path = Path(folder_path_str_formatted)

    if not folder_path.is_dir():
        raise ValueError(
            f"Folder path '{folder_path_str}' does not exist. Please try a different path."
        )

    return folder_path


def get_user_info_api_key() -> None:
    message = "Please enter your API key from ANT"
    api_key = prompt_user_for_info("api_key", message)

    if api_key:
        set_key(
            dotenv_path=ENV_FILE_PATH,
            key_to_set="API_KEY",
            value_to_set=api_key,
        )
    else:
        raise ValueError("No API key was set - please restart")


def load_env_file() -> tuple[str, list[Path], Path]:
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
