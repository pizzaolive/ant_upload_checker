import pytest
from pathlib import Path
import ant_upload_checker.film_processing as funcs
import pandas as pd


@pytest.fixture
def test_extras_file_paths():
    test_paths = [
        "C:/The Extras 2030/The Extras 2030.mkv",
        "C:/The Extras 2030/Extras/Bloopers.mkv",
        "C:/Godzilla: King of the Monsters (2019)/Godzilla: King of the Monsters (2019).mkv",
        "C:/Godzilla: King of the Monsters (2019)/Extras/Godzilla extras (2019).mkv",
        "C:/Godzilla: King of the Monsters (2019)/Extras/Godzilla: King of the Monsters (2019).mkv",
    ]
    test_paths = [Path(x) for x in test_paths]
    return test_paths


def test_remove_paths_containing_extras_folder(test_extras_file_paths):
    actual_list = funcs.remove_paths_containing_extras_folder(test_extras_file_paths)

    expected_list = [
        "C:/The Extras 2030/The Extras 2030.mkv",
        "C:/Godzilla: King of the Monsters (2019)/Godzilla: King of the Monsters (2019).mkv",
    ]
    expected_list = [Path(x) for x in expected_list]

    assert actual_list == expected_list


@pytest.fixture
def test_film_paths():
    test_list = [
        "C:/Atlantics (2019)/Atlantique.2019.mkv",
        "C:/tick tick... BOOM! 2021 test.mkv",
        "C:/Da.5.Bloods.2020.test.mkv",
        "C:/Short term 12 2013/Short term 12 2013 film info.mkv",
        "C:/X: First Class (2100)",
        "C:/Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
        "C:/L.A. Confidential (1997) test.mkv",
        "C:/A.I. Artificial Intelligence (2100)",
        "C:/G.I. Jane (2100)",
        "C:/E.T. the Extra-Terrestrial (2100)",
        "C:/S.W.A.T. (2100)",
        "C:/T.E.S. Test film (2010)",
        "C:/T.E.S.T. Test film (2010)",
    ]
    test_list = [Path(x) for x in test_list]

    return test_list


def test_get_film_title_from_path(test_film_paths):
    # Note the issues with some acronyms with guessit
    # Note path parent folder is taken e.g. Atlantics instead of Atlantique
        # Where the year is in brackets ()

    actual_list = [funcs.get_film_title_from_path(x) for x in test_film_paths]
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

    actual_list = [funcs.fix_title_if_contains_acronym(x) for x in test_list]

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
    actual_list = funcs.get_formatted_titles_from_film_paths(test_film_paths)

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
    test_film_titles = [
        Path("C:/Short term 12 2013/Short term 12 2013 film info.mkv"),
        Path("C:/X: First Class (2100)"),
    ]
    test_film_titles = ["Short term 12", "X: First Class"]

    actual_df = funcs.create_film_list_dataframe(test_film_titles, test_film_titles)

    expected_df = pd.DataFrame(
        {"Full file path": test_film_titles, "Parsed film title": test_film_titles}
    ).astype(str)

    pd.testing.assert_frame_equal(actual_df, expected_df)
