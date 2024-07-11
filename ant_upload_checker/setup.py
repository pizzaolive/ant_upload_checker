import logging
import inquirer
from pathlib import Path
from dotenv import set_key
from typing import List


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_user_information() -> List[str]:
    prompts = [inquirer.Text("api_key", message="Please enter your API key from ANT")]

    responses = inquirer.prompt(prompts)

    save_user_info_to_dot_env(responses)

    return responses


def save_user_info_to_dot_env(user_info: List[str]) -> None:
    env_file_path = Path(".env").resolve()
    env_file_path.touch()
    set_key(
        dotenv_path=env_file_path,
        key_to_set="API_KEY",
        value_to_set=user_info["api_key"],
    )
