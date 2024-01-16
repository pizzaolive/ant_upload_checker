import ant_upload_checker.film_processing as funcs
import pandas as pd
from pathlib import Path


def test_add_film_name_column():
    test_df = pd.DataFrame(
        {
            "full path": [
                r"C:\Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
                r"C:\L.A. Confidential (1997) test.mkv",
                r"C:\tick tick. BOOM! 2021 test.mkv",
                r"C:\Da.5.Bloods.2020.test.mkv",
                r"C:\Short term 12 2013\Short term 12 2013 film info.mkv",
            ],
            "file name": [
                r"Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
                "L.A. Confidential (1997) test.mkv",
                "tick tick. BOOM! 2021 test....",
                "Da.5.Bloods.2020.test.mkv",
                "Short term 12 2013 film info.mkv.",
            ],
        }
    )

    actual_df = funcs.add_film_name_column(test_df)
    expected_df = pd.DataFrame(
        {
            "full path": [
                r"C:\Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
                r"C:\L.A. Confidential (1997) test.mkv",
                r"C:\tick tick. BOOM! 2021 test.mkv",
                r"C:\Da.5.Bloods.2020.test.mkv",
                r"C:\Short term 12 2013\Short term 12 2013 film info.mkv",
            ],
            "file name": [
                r"Nick Fury: Agent of S.H.I.E.L.D. (1998).mkv",
                "L.A. Confidential (1997) test.mkv",
                "tick tick. BOOM! 2021 test....",
                "Da.5.Bloods.2020.test.mkv",
                "Short term 12 2013 film info.mkv.",
            ],
            "film name": [
                "Nick Fury: Agent of S.H.I.E.L.D.",
                "L.A. Confidential",
                "tick tick. BOOM!",
                "Da 5 Bloods",
                "Short term 12",
            ],
        }
    )

    pd.testing.assert_frame_equal(actual_df, expected_df)


def test_remove_edition_info():
    test_series = pd.DataFrame(
        {
            "file name": [
                "Test film extended cut (2020)",
                "Test film theatrical cut 2020",
                "test film THEATrical cut 2019",
                "Test film EXTended cut 2020",
                "Extended arm film 2020",
            ],
        }
    )

    actual_df = funcs.remove_edition_info(test_series)
    expected_df = pd.DataFrame(
        {
            "file name": [
                "Test film (2020)",
                "Test film 2020",
                "test film 2019",
                "Test film 2020",
                "Extended arm film 2020",
            ],
        }
    )

    pd.testing.assert_frame_equal(actual_df, expected_df)


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
