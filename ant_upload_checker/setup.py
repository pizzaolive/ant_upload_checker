import logging
import os
import inquirer
from pathlib import Path
from dotenv import set_key, load_dotenv
import tkinter
import tkfilebrowser
from typing import List, Tuple

ENV_FILE_PATH = Path(".env").resolve()


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def check_if_user_wants_to_override_env_file():
    question = [
        inquirer.List(
            "choice",
            message="An API key was already found, do you want to overwrite this?",
            choices=["Yes", "No"],
            default="No",
        )
    ]
    response = inquirer.prompt(question)

    if response["choice"] == "Yes":
        return True
    return False


def get_user_information() -> List[str]:
    if not ENV_FILE_PATH.is_file() or check_if_user_wants_to_override_env_file():
        get_user_input_api_key(ENV_FILE_PATH)

    get_input_folders()


def get_input_folders() -> Tuple[str]:
    root = tkinter.Tk()
    root.withdraw()
    logging.info(
        "In the dialog box, please select one or more directories containing your films"
    )
    directories = tkfilebrowser.askopendirnames(
        title="Select one or more directories containing your films"
    )
    root.destroy()

    directories_str = ",".join(directories)

    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="INPUT_FOLDERS",
        value_to_set=directories_str,
    )


def get_user_input_api_key() -> List[str]:
    prompt = [inquirer.Text("api_key", message="Please enter your API key from ANT")]

    user_api_key = inquirer.prompt(prompt)

    save_user_info_to_dot_env(user_api_key)


def save_user_info_to_dot_env(user_info: List[str]) -> None:
    ENV_FILE_PATH.touch()
    set_key(
        dotenv_path=ENV_FILE_PATH,
        key_to_set="API_KEY",
        value_to_set=user_info["api_key"],
    )


def load_existing_env_file():
    load_dotenv(ENV_FILE_PATH)

    api_key = os.getenv("API_KEY")

    input_folders = os.getenv("INPUT_FOLDERS").split(",")
    input_folders = [Path(folder) for folder in input_folders]

    return api_key, input_folders
