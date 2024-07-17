import logging
import inquirer
from pathlib import Path
from dotenv import set_key
import tkinter
import tkfilebrowser
from typing import List, Tuple


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
    env_file_path = Path(".env")
    if not env_file_path.is_file() or check_if_user_wants_to_override_env_file():
        get_user_input_api_key()

    get_input_folders()


def get_input_folders() -> Tuple[str]:
    root = tkinter.Tk()
    root.withdraw()
    logging.info("Please select the directory containing your films in the dialog box")
    directories = tkfilebrowser.askopendirnames(
        title="Please select where your films are stored"
    )
    root.destroy()

    return directories


def get_user_input_api_key() -> List[str]:
    prompt = [inquirer.Text("api_key", message="Please enter your API key from ANT")]

    user_api_key = inquirer.prompt(prompt)

    save_user_info_to_dot_env(user_api_key)


def save_user_info_to_dot_env(user_info: List[str]) -> None:
    env_file_path = Path(".env").resolve()
    env_file_path.touch()
    set_key(
        dotenv_path=env_file_path,
        key_to_set="API_KEY",
        value_to_set=user_info["api_key"],
    )
