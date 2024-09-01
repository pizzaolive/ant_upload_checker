from ant_upload_checker.dupe_checker import DupeChecker
import pandas as pd
import pytest


test_values = [
    ("file_path", "1080p", "H264", "Blu-ray", "group", []),
    (
        "C:/films/test_film_name.mkv",
        "1080p",
        "H264",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [{"size": "100", "name": "test_film_name.mkv"}],
            }
        ],
    ),
    (
        "C:/films/test_film_name_2.mkv",
        "1080p",
        "H264",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link_2",
                "files": [
                    {"size": "1", "name": "unwanted_file.nfo"},
                    {"size": "100", "name": "test_film_name_2.mkv"},
                ],
            }
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "720p",
        "H264",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_filmy.mkv"},
                ],
                "resolution": "720p",
                "codec": "H265",
                "media": "Blu-ray",
            },
            {  # duplicate resolution, codec, source
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_different_name.mkv"},
                ],
                "resolution": "720p",
                "codec": "H264",
                "media": "Blu-ray",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "2160p",
        "H265",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "2160p",
                "codec": "H265",
                "media": "BLU-RAY",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "2160p",
        "H265",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "2160p",
                "codec": "H264",  # not a dupe, as codec differs
                "media": "Blu-ray",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "1080p",
        "H264",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "2160p",  # not a dupe, as resolution differs
                "codec": "H264",
                "media": "Blu-ray",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "",  # missing resolution from guessed film
        "H264",
        "Blu-ray",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "1080p",
                "codec": "H264",
                "media": "Blu-ray",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "1080p",
        "",  # missing codec from guessed film
        "",  # missing source from guessed film
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "1080p",
                "codec": "H264",
                "media": "Blu-ray",
            },
        ],
    ),
    (
        "C:/films/testing_film.mkv",
        "",  # missing
        "",  # missing codec from guessed film
        "Web",
        "group",
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "testing_film_non_exact_filename_match.mkv"},
                ],
                "resolution": "1080p",
                "codec": "H264",
                "media": "WEB",
            },
        ],
    ),
    (
        "C:/films/test_film_name.mkv",
        "1080p",
        "H264",
        "Blu-ray",
        "KiNGDOM",
        [
            {
                "guid": "test_link",
                "files": [{"size": "100", "name": "test_film_name.mkv"}],
            }
        ],
    ),
]
expected_values = [
    "NOT FOUND",
    "Duplicate: exact filename already exists: test_link",
    "Duplicate: exact filename already exists: test_link_2",
    "Duplicate: a film with 720p/H264/Blu-ray already exists: test_link",
    "Duplicate: a film with 2160p/H265/Blu-ray already exists: test_link",
    "Not a duplicate: a film with 2160p/H265/Blu-ray does not already exist. test_link",
    "Not a duplicate: a film with 1080p/H264/Blu-ray does not already exist. test_link",
    "Partial duplicate: a film with H264/Blu-ray already exists. Could not extract and check resolution from filename. test_link",
    "Partial duplicate: a film with 1080p already exists. Could not extract and check codec/media from filename. test_link",
    "Partial duplicate: a film with Web already exists. Could not extract and check resolution/codec from filename. test_link",
    "Release group 'KiNGDOM' is banned from ANT - do not upload",
]


@pytest.mark.parametrize(
    ("test_input", "test_output"),
    zip(test_values, expected_values),
)
def test_check_if_film_is_duplicate(test_input, test_output):
    dupe_checker = DupeChecker(pd.DataFrame())

    actual_return = dupe_checker.check_if_film_is_duplicate(
        test_input[0],
        test_input[1],
        test_input[2],
        test_input[3],
        test_input[4],
        test_input[5],
    )

    assert actual_return == test_output
