import pytest
from ant_upload_checker import setup_functions
from pathlib import Path
import inquirer


def test_return_as_path_if_valid(tmp_path):
    actual_return = setup_functions.return_as_path_if_valid(tmp_path)
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


def test_get_user_input_folders(monkeypatch, tmp_path):
    temp_paths = [tmp_path / "Films", tmp_path / "Old films"]
    [folder.mkdir() for folder in temp_paths]

    temp_paths_str = [str(temp_path) for temp_path in temp_paths]

    def mock_prompt(_):
        return {"input_folders": ",".join(temp_paths_str)}

    monkeypatch.setattr(inquirer, "prompt", mock_prompt)

    actual_return = setup_functions.get_user_input_folders()
    expected_return = [Path(folder) for folder in temp_paths]

    assert actual_return == expected_return
