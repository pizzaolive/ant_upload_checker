import pytest
import logging
from pathlib import Path
from ant_upload_checker.film_processor import FilmProcessor
import pandas as pd
import numpy as np

LOGGER = logging.getLogger(__name__)


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
        r"C:/Atlantics (2019)/Atlantique.2019.mkv",
        r"C:/tick tick... BOOM! 2021 test.mkv",
        r"C:/Da.5.Bloods.2020.test.mkv",
        r"C:/Short term 12 2013/Short term 12 2013 film info.mkv",
        r"C:/X: First Class (2100)",
        r"C:/Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
        r"C:/L.A. Confidential (1997) test.mkv",
        r"C:/A.I. Artificial Intelligence (2100)",
        r"C:/G.I. Jane (2100)",
        r"C:/E.T. the Extra-Terrestrial (2100)",
        r"C:/S.W.A.T. (2100)",
        r"C:/T.E.S. Test film (2010)",
        r"C:/T.E.S.T. Test film (2010)",
    ]
    test_list = [Path(x) for x in test_list]

    return test_list


def test_get_film_title_from_path(test_film_paths):
    # Note the issues with some acronyms with guessit
    # Note path parent folder is taken e.g. Atlantics instead of Atlantique
    # Where the year is in brackets ()
    fp = FilmProcessor("test", "test")

    actual_list = [fp.get_film_title_from_path(x) for x in test_film_paths]
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


def test_get_formatted_titles_from_film_paths(test_film_paths):
    fp = FilmProcessor("test", "test")
    actual_list = fp.get_formatted_titles_from_film_paths(test_film_paths)

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


def test_create_film_list_dataframe():
    fp = FilmProcessor("test", "test")
    test_film_paths = [
        Path(r"C:\X: First Class (2100)"),
        Path(r"C:\Short term 12 2013\Short term 12 2013 film info.mkv"),
    ]
    test_film_titles = ["X: First Class", "Short term 12"]
    test_film_sizes = [5.11, 2.14]

    actual_df = fp.create_film_list_dataframe(
        test_film_paths, test_film_sizes, test_film_titles
    )

    expected_df = pd.DataFrame(
        {
            "Full file path": [
                r"C:\X: First Class (2100)",
                r"C:\Short term 12 2013\Short term 12 2013 film info.mkv",

            ],
            "Film size (GB)": [5.11,2.14],
            "Parsed film title": ["X: First Class","Short term 12"],
            "Already on ANT?": [np.nan, np.nan],
        }
    )

    pd.testing.assert_frame_equal(actual_df, expected_df)


def test_convert_bytes_to_gb():
    fp = FilmProcessor("test", "test")
    test_list = [1073741824, 1610612736, 1309965025]
    actual_list = [fp.convert_bytes_to_gb(num) for num in test_list]
    expected_list = [1, 1.5, 1.22]

    assert actual_list == expected_list


def test_false_get_existing_film_list_if_exists(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)

    assert fp.get_existing_film_list_if_exists() == False
    assert "An existing output file" in caplog.text


def test_true_get_existing_film_list_if_exists(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    test_df = pd.DataFrame(
        {
            "Full file path": ["test"],
            "Film size (GB)": 10.11,
            "Parsed film title": "test",
        }
    )
    test_df.to_csv(tmp_path.joinpath("Film list.csv"), index=False)

    fp = FilmProcessor(input_folders="", output_folder=tmp_path)
    actual_return_value = fp.get_existing_film_list_if_exists()

    expected_df = pd.DataFrame(
        {
            "Full file path": ["test"],
            "Film size (GB)": 10.11,
            "Parsed film title": "test",
        }
    )

    pd.testing.assert_frame_equal(actual_return_value, expected_df)
