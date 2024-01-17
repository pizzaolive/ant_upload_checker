import ant_upload_checker.film_processing as funcs
import pandas as pd
from pathlib import Path


def test_remove_paths_containing_extras_folder():
    test_paths = [
        "C:\The Extras 2030\The Extras 2030.mkv",
        "C:\The Extras 2030\Extras\Bloopers.mkv",
        "C:\Godzilla: King of the Monsters (2019)\Godzilla: King of the Monsters (2019).mkv",
        "C:\Godzilla: King of the Monsters (2019)\Extras\Godzilla extras (2019).mkv",
        "C:\Godzilla: King of the Monsters (2019)\Extras\Godzilla: King of the Monsters (2019).mkv",
    ]
    test_paths = [Path(x) for x in test_paths]

    actual_list = funcs.remove_paths_containing_extras_folder(test_paths)

    expected_list = [
        "C:\The Extras 2030\The Extras 2030.mkv",
        "C:\Godzilla: King of the Monsters (2019)\Godzilla: King of the Monsters (2019).mkv",
    ]
    expected_list = [Path(x) for x in expected_list]

    assert actual_list == expected_list


def test_get_titles_from_film_paths():
    test_list = [
        "C:/Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
        "C:/L.A. Confidential (1997) test.mkv",
        "C:/tick tick... BOOM! 2021 test.mkv",
        "C:/Da.5.Bloods.2020.test.mkv",
        "C:/Short term 12 2013/Short term 12 2013 film info.mkv",
    ]
    test_list = [Path(x) for x in test_list]

    actual_list = funcs.get_titles_from_film_paths(test_list)

    expected_list = [
        "Nick Fury: Agent of S.H.I.E.L.D.",
        "L.A. Confidential",
        "tick tick BOOM!",
        "Da 5 Bloods",
        "Short term 12",
    ]

    assert actual_list == expected_list


def test_fix_title_if_contains_acronym():
    test_list = [
        "X: First Class",
        "A normal film with I am",
        "L A Confidential",
        "A I Artificial Intelligence",
        "G I Jane",
        "Agents of S H I E L D",
        "Agents of S.H.I.E.L.D.",
        "E T the Extra-Terrestrial",
        "S W A T",
        "S.W.A.T.",
    ]

    actual_list = [funcs.fix_title_if_contains_acronym(x) for x in test_list]

    expected_list = [
        "X: First Class",
        "A normal film with I am",
        "L.A. Confidential",
        "A.I. Artificial Intelligence",
        "G.I. Jane",
        "Agents of S.H.I.E.L.D.",
        "Agents of S.H.I.E.L.D.",
        "E.T. the Extra-Terrestrial",
        "S.W.A.T.",
        "S.W.A.T.",
    ]

    assert actual_list == expected_list
