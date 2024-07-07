import pytest
import logging
from pathlib import Path
from ant_upload_checker.film_processor import FilmProcessor
import pandas as pd
import numpy as np
from collections import OrderedDict

LOGGER = logging.getLogger(__name__)


def test_get_film_file_paths(tmp_path):
    temp_mp4_file = tmp_path / "test.mp4"
    temp_mp4_file.write_text("Test")

    temp_extras_directory = tmp_path / "Extras"
    temp_extras_directory.mkdir()
    temp_mp4_file_to_be_removed = tmp_path / "Extras" / "test_2.mp4"
    temp_mp4_file_to_be_removed.write_text("Test")

    fp = FilmProcessor(input_folders=[tmp_path.parent], output_folder="")

    actual_output = fp.get_film_file_paths()
    expected_output = [temp_mp4_file]

    assert actual_output == expected_output


@pytest.fixture
def test_extras_file_paths():
    test_paths = [
        r"C:/The Extras 2030/The Extras 2030.mkv",
        r"C:/The Extras 2030/Extras/Bloopers.mkv",
        r"C:/Godzilla: King of the Monsters (2019)/Godzilla: King of the Monsters (2019).mkv",
        r"C:/Godzilla: King of the Monsters (2019)/Extras/Godzilla extras (2019).mkv",
        r"C:/Godzilla: King of the Monsters (2019)/Extras/Godzilla: King of the Monsters (2019).mkv",
    ]
    test_paths = [Path(x) for x in test_paths]
    return test_paths


def test_remove_paths_containing_extras_folder(test_extras_file_paths):
    fp = FilmProcessor("test", "test")
    actual_list = fp.remove_paths_containing_extras_folder(test_extras_file_paths)

    expected_list = [
        r"C:/The Extras 2030/The Extras 2030.mkv",
        r"C:/Godzilla: King of the Monsters (2019)/Godzilla: King of the Monsters (2019).mkv",
    ]
    expected_list = [Path(x) for x in expected_list]

    assert actual_list == expected_list


@pytest.fixture
def test_film_paths():
    test_list = [
        r"C:/Atlantics (2019)/Atlantique.2019.2160p.mkv",
        r"C:/tick tick... BOOM! 2021 test.720p.mkv",
        r"C:/Da.5.Bloods.2020..1080p.test.mkv",
        r"C:/Short term 12 2013/Short term 12 2013.1080p.film info.mkv",
        r"C:/X: First Class (2100).1080p.mkv",
        r"C:/Nick Fury: Agent of S.H.I.E.L.D. (1998).1080p.mkv",
        r"C:/L.A. Confidential (1997) .1080p.mkv",
        r"C:/A.I. Artificial Intelligence (2100).1080p.mkv",
        r"C:/G.I. Jane (2100).mkv",
        r"C:/E.T. the Extra-Terrestrial (2100).1080p.mkv",
        r"C:/S.W.A.T. (2100).1080p.mkv",
        r"C:/T.E.S. Test film (2010).1080p.mkv",
        r"C:/T.E.S.T. Test film (2010).1080p.mkv",
    ]
    test_list = [Path(x) for x in test_list]

    return test_list


@pytest.fixture
def test_guessit_films():
    test_guessit_films = [
        {"title": "Atlantics", "screen_size": "2160p"},
        {"title": "tick tick BOOM!", "screen_size": "720p"},
        {"title": "Da 5 Bloods", "screen_size": "1080p"},
        {"title": "Short term 12", "screen_size": "1080p"},
        {"title": "X: First Class", "screen_size": "1080p"},
        {"title": "Nick Fury: Agent of S.H.I.E.L.D.", "screen_size": "1080p"},
        {"title": "L A Confidential", "screen_size": "1080p"},
        {"title": "A I Artificial Intelligence", "screen_size": "1080p"},
        {"title": "G I Jane"},
        {"title": "E T the Extra-Terrestrial", "screen_size": "1080p"},
        {"title": "S.W.A.T.", "screen_size": "1080p"},
        {"title": "T E S Test film", "screen_size": "1080p"},
        {"title": "T E.S.T Test film", "screen_size": "1080p"},
    ]
    ordered_dict_guessit_films = [OrderedDict(x) for x in test_guessit_films]

    return ordered_dict_guessit_films


def test_get_guessit_info_from_film_paths(test_film_paths):
    fp = FilmProcessor("test", "test")
    actual_guessit_films = fp.get_guessit_info_from_film_paths(test_film_paths)

    expected_type = OrderedDict
    assert all([isinstance(x, expected_type) for x in actual_guessit_films])


def test_get_film_attribitue_from_guessed_film(test_guessit_films):
    fp = FilmProcessor("test", "test")

    actual_list = [
        fp.get_film_attribute_from_guessed_film(x, "title") for x in test_guessit_films
    ]
    expected_list = [
        "Atlantics",
        "tick tick BOOM!",
        "Da 5 Bloods",
        "Short term 12",
        "X: First Class",
        "Nick Fury: Agent of S.H.I.E.L.D.",
        "L A Confidential",
        "A I Artificial Intelligence",
        "G I Jane",
        "E T the Extra-Terrestrial",
        "S.W.A.T.",
        "T E S Test film",
        "T E.S.T Test film",
    ]

    assert actual_list == expected_list


def test_fix_title_if_contains_acronym():
    fp = FilmProcessor("test", "test")

    test_list = [
        "Atlantics",
        "tick tick BOOM!",
        "Da 5 Bloods",
        "Short term 12",
        "X: First Class",
        "Nick Fury: Agent of S.H.I.E.L.D.",
        "L A Confidential",
        "A I Artificial Intelligence",
        "G I Jane",
        "E T the Extra-Terrestrial",
        "S.W.A.T.",
        "T E S Test film",
        "T E.S.T Test film",
    ]

    actual_list = [fp.fix_title_if_contains_acronym(x) for x in test_list]

    expected_list = [
        "Atlantics",
        "tick tick BOOM!",
        "Da 5 Bloods",
        "Short term 12",
        "X: First Class",
        "Nick Fury: Agent of S.H.I.E.L.D.",
        "L.A. Confidential",
        "A.I. Artificial Intelligence",
        "G.I. Jane",
        "E.T. the Extra-Terrestrial",
        "S.W.A.T.",
        "T.E.S. Test film",
        "T.E.S.T. Test film",
    ]

    assert actual_list == expected_list


def test_get_formatted_titles_from_guessed_films(test_guessit_films):
    fp = FilmProcessor("test", "test")
    actual_list = fp.get_formatted_titles_from_guessed_films(test_guessit_films)

    expected_list = [
        "Atlantics",
        "tick tick BOOM!",
        "Da 5 Bloods",
        "Short term 12",
        "X: First Class",
        "Nick Fury: Agent of S.H.I.E.L.D.",
        "L.A. Confidential",
        "A.I. Artificial Intelligence",
        "G.I. Jane",
        "E.T. the Extra-Terrestrial",
        "S.W.A.T.",
        "T.E.S. Test film",
        "T.E.S.T. Test film",
    ]

    assert actual_list == expected_list


def test_get_film_resolutions_from_guessed_film(test_guessit_films):
    fp = FilmProcessor("test", "test")
    actual_list = fp.get_film_resolutions_from_guessed_films(test_guessit_films)
    expected_list = [
        "2160p",
        "720p",
        "1080p",
        "1080p",
        "1080p",
        "1080p",
        "1080p",
        "1080p",
        "",  # File name for G.I. Jane has no resolution - expect ""
        "1080p",
        "1080p",
        "1080p",
        "1080p",
    ]

    assert actual_list == expected_list


def test_create_film_list_dataframe():
    fp = FilmProcessor("test", "test")
    test_film_paths = [
        Path(r"C:\X: First Class (2100)"),
        Path(r"C:\Short term 12 2013\Short term 12 2013 film info.mkv"),
    ]
    test_film_titles = ["X: First Class", "Short term 12"]
    test_film_sizes = [5.11, 2.14]
    test_film_codecs = ["", ""]
    test_film_sources = ["Blu-ray", "Web"]
    test_film_resolutions = ["1080p", "1080p"]
    test_release_groups = ["", ""]

    actual_df = fp.create_film_list_dataframe(
        test_film_paths,
        test_film_sizes,
        test_film_titles,
        test_film_resolutions,
        test_film_codecs,
        test_film_sources,
        test_release_groups,
    )

    expected_df = pd.DataFrame(
        {
            "Full file path": [
                r"C:\X: First Class (2100)",
                r"C:\Short term 12 2013\Short term 12 2013 film info.mkv",
            ],
            "Parsed film title": ["X: First Class", "Short term 12"],
            "Film size (GB)": [5.11, 2.14],
            "Resolution": ["1080p", "1080p"],
            "Codec": ["", ""],
            "Source": ["Blu-ray", "Web"],
            "Release group": ["", ""],
            "Already on ANT?": [pd.NA, pd.NA],
        }
    ).astype(
        {
            "Full file path": "string",
            "Parsed film title": "string",
            "Film size (GB)": "float64",
            "Resolution": "string",
            "Codec": "string",
            "Source": "string",
            "Release group": "string",
            "Already on ANT?": "string",
        }
    )

    pd.testing.assert_frame_equal(actual_df, expected_df)


def test_convert_bytes_to_gb():
    fp = FilmProcessor("test", "test")
    test_list = [1073741824, 1610612736, 1309965025]
    actual_list = [fp.convert_bytes_to_gb(num) for num in test_list]
    expected_list = [1, 1.5, 1.22]

    assert actual_list == expected_list


def test_combine_current_film_list_with_existing_csv(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    test_existing_film_df = pd.DataFrame(
        {
            "Full file path": ["test_path"],
            "Parsed film title": ["test"],
            "Film size (GB)": [10.4],
            "Resolution": ["test"],
            "Codec": ["test"],
            "Source": ["test"],
            "Release group": ["test"],
            "Already on ANT?": ["NOT FOUND"],
        }
    )
    test_existing_film_df.to_csv(tmp_path.joinpath("Film list.csv"), index=False)

    test_current_film_list = pd.DataFrame(
        {
            "Full file path": ["test_path", "New film"],
            "Parsed film title": ["test", "New film"],
            "Film size (GB)": [10.4, 9.9],
            "Resolution": ["test", "test"],
            "Codec": ["test", "test"],
            "Source": ["test", "test"],
            "Release group": ["test", "test"],
            "Already on ANT?": [pd.NA, pd.NA],
        }
    ).astype(
        {
            "Full file path": "string",
            "Parsed film title": "string",
            "Film size (GB)": "float64",
            "Resolution": "string",
            "Codec": "string",
            "Source": "string",
            "Release group": "string",
            "Already on ANT?": "string",
        }
    )

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)

    actual_df = fp.combine_current_film_list_with_existing_csv(
        test_existing_film_df, test_current_film_list
    )

    expected_df = pd.DataFrame(
        {
            "Full file path": [
                "New film",
                "test_path",
            ],
            "Parsed film title": ["New film", "test"],
            "Film size (GB)": [9.9, 10.4],
            "Resolution": ["test", "test"],
            "Codec": ["test", "test"],
            "Source": ["test", "test"],
            "Release group": ["test", "test"],
            "Already on ANT?": [pd.NA, "NOT FOUND"],
        }
    ).astype(
        {
            "Full file path": "string",
            "Parsed film title": "string",
            "Film size (GB)": "float64",
            "Resolution": "string",
            "Codec": "string",
            "Source": "string",
            "Release group": "string",
            "Already on ANT?": "string",
        }
    )

    pd.testing.assert_frame_equal(actual_df, expected_df)


def test_check_if_existing_film_csv_exists(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)

    test_existing_film_df = pd.DataFrame(
        {
            "Full file path": [pd.NA],
            "Parsed film title": [pd.NA],
            "Film size (GB)": [pd.NA],
            "Codec": [pd.NA],
            "Source": [pd.NA],
            "Release group": [pd.NA],
            "Already on ANT?": [pd.NA],
        }
    )
    path_name = tmp_path.joinpath("Film list.csv")
    test_existing_film_df.to_csv(path_name, index=False)

    assert fp.check_if_existing_film_csv_exists() is True
    assert f"An existing output file ({path_name}) was found" in caplog.text


def test_false_check_if_existing_film_csv_exists(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)
    path_name = tmp_path.joinpath("Film list.csv")

    assert fp.check_if_existing_film_csv_exists() is False
    assert (
        f"An existing output file ({path_name}) was not found, processing films from scratch..."
        in caplog.text
    )


def test_false_check_if_existing_csv_is_compatible(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)

    # Resolution is missing from existing film list
    test_existing_film_df = pd.DataFrame(
        {
            "Full file path": [pd.NA],
            "Parsed film title": [pd.NA],
            "Film size (GB)": [pd.NA],
            "Codec": [pd.NA],
            "Source": [pd.NA],
            "Release group": [pd.NA],
            "Already on ANT?": [pd.NA],
        }
    )
    test_existing_film_df.to_csv(tmp_path.joinpath("Film list.csv"), index=False)

    assert fp.check_if_existing_csv_is_compatible(test_existing_film_df) is False
    assert (
        "Warning: existing file was created using an old version of ANT upload checker"
        in caplog.text
    )
    assert Path.is_file(tmp_path.joinpath("Film list old version backup.csv"))


def test_true_check_if_existing_csv_is_compatible(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    test_existing_film_df = pd.DataFrame(
        {
            "Full file path": [pd.NA],
            "Parsed film title": [pd.NA],
            "Film size (GB)": [pd.NA],
            "Resolution": [pd.NA],
            "Codec": [pd.NA],
            "Source": [pd.NA],
            "Release group": [pd.NA],
            "Already on ANT?": [pd.NA],
        }
    )
    test_existing_film_df.to_csv(tmp_path.joinpath("Film list.csv"), index=False)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)

    assert fp.check_if_existing_csv_is_compatible(test_existing_film_df) is True
    assert not Path.is_file(tmp_path.joinpath("Film list old version backup.csv"))
