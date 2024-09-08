import pytest
from ant_upload_checker import setup_functions
from pathlib import Path
import inquirer


def test_return_as_path_if_valid(tmp_path):
    temp_path_str = str(tmp_path)
    actual_return = setup_functions.return_as_path_if_valid(temp_path_str)
    assert isinstance(actual_return, Path)


def test_return_as_path_if_valid_bad_file_path():
    test_incorrect_path = "C:/Media/Fake_path"
    with pytest.raises(
        ValueError,
        match="Folder path 'C:/Media/Fake_path' does not exist. Please try a different path.",
    ):
        setup_functions.return_as_path_if_valid(test_incorrect_path)


def test_return_as_path_if_valid_none():
    with pytest.raises(
        ValueError,
        match="No folder path was selected in the dialog box, please re-run",
    ):
        setup_functions.return_as_path_if_valid(None)


TEST_INPUT_PATHS = [["Films", "Old films"], ["Single film folder"]]


@pytest.mark.parametrize("test_paths", TEST_INPUT_PATHS)
def test_get_user_input_folders(monkeypatch, tmp_path, test_paths):
    temp_paths = [tmp_path / path for path in test_paths]
    [folder.mkdir() for folder in temp_paths]

    temp_paths_str = [str(temp_path) for temp_path in temp_paths]

    def mock_prompt(_):
        # Note empty space that should be removed
        return {"input_folders": ", ".join(temp_paths_str)}

    monkeypatch.setattr(inquirer, "prompt", mock_prompt)

    actual_return = setup_functions.get_user_input_folders()
    expected_return = [str(folder) for folder in temp_paths]

    assert actual_return == expected_return


def test_get_user_output_folder(monkeypatch, tmp_path):
    temp_path = tmp_path / "Media"
    temp_path.mkdir()

    temp_path_str = str(temp_path)

    def mock_prompt(_):
        # Empty space before path should be removed
        return {"output_folder": f" {temp_path_str}"}

    monkeypatch.setattr(inquirer, "prompt", mock_prompt)

    actual_return = setup_functions.get_user_output_folder()
    expected_return = temp_path_str

    assert actual_return == expected_return


def test_get_user_info_api_key_empty(monkeypatch):
    with pytest.raises(ValueError, match="No API key was set - please restart"):

        def mock_prompt(_):
            return {"api_key": ""}

        monkeypatch.setattr(inquirer, "prompt", mock_prompt)

        setup_functions.get_user_info_api_key()
