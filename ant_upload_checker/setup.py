import logging
import os
import inquirer
from pathlib import Path
from dotenv import set_key, dotenv_values
import tkinter
import tkfilebrowser
from typing import List, Tuple

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
        get_user_info_input_folders()
        get_user_info_output_folder()
        logging.info("User setting saved to '.env' file")


def get_user_info_input_folders() -> None:
    root = tkinter.Tk()
    root.withdraw()
    logging.info(
        "In the dialog box, please select one or more directories containing your films"
    )
    directories = tkfilebrowser.askopendirnames(
        title="Select one or more directories containing your films"
    )
    root.destroy()

    if directories:
        directories_str = ",".join(directories)
        set_key(
            dotenv_path=ENV_FILE_PATH,
            key_to_set="INPUT_FOLDERS",
            value_to_set=directories_str,
        )
    else:
        raise ValueError("No input directories were selected - please restart")


def get_user_info_output_folder() -> None:
    root = tkinter.Tk()
    root.withdraw()
    logging.info(
        "In the dialog box, please select your output directory (where the film list will be saved)"
    )

    directory = tkfilebrowser.askopendirname(title="Select an output directory")
    root.destroy()

    if directory:
        set_key(
            dotenv_path=ENV_FILE_PATH,
            key_to_set="OUTPUT_FOLDER",
            value_to_set=directory,
        )
    else:
        raise ValueError("No output directory was selected - please restart")


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


def load_env_file() -> Tuple[str, List[Path], Path]:
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

    logging.info("User settings loaded from '.env' file")

    return api_key, input_folders, output_folder
