import pandas as pd
import numpy as np
import pytest
import logging
from ant_upload_checker.film_searcher import FilmSearcher

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def return_mock_search_for_film_on_ant_not_found(monkeypatch):
    def mockreturn(test_arg, test_arg_2):
        return []

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )


@pytest.fixture
def return_mock_search_for_film_on_ant_torrentid(monkeypatch):
    def mockreturn(test_arg, test_arg_2):
        return [{"guid": "url/torrentid=1"}]

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )


def test_check_if_films_exist_on_ant(
    return_mock_search_for_film_on_ant_not_found, caplog
):
    # pre dupe check, torrentid links would be skipped from searching
    # post 1.7.0, films are only skipped from searching
    # if start with Duplicate:
    # (as these may have since been uploaded by others)

    caplog.set_level(logging.INFO)

    test_df = pd.DataFrame(
        {
            "Full file path": [
                "C:/Movies/Test (2020)/Test (2020).mkv",
                "C:/Movies/Another film (2020)/Another film (2020).mkv",
                "C:/Movies/Test film (2020)/Test film (2020).mkv",
                "C:/Movies/New film (2020)/New film (2020).mkv",
                "C:/Movies/An awesome test film 1080p H264 Web-DL (2020).mkv",
                "C:/Movies/Batman Begins 2160p H265 Blu-ray (2005).mkv",
                "C:/Movies/zebras",
            ],
            "Film size (GB)": [1.11, 1.22, 1.33, 1.44, 2.0, 5.0, 1.0],
            "Parsed film title": [
                "Test",
                "Another film",
                "test film",
                "New film",
                "An awesome test film",
                "Batman Begins",
                "zebras",
            ],
            "Resolution": ["1080p", "1080p", "1080p", "1080p", "1080p", "2160p", ""],
            "Codec": ["H264", "H264", "H264", "H264", "H264", "H265", ""],
            "Source": ["Blu-ray", "Blu-ray", "Blu-ray", "Web", "Web", "Blu-ray", ""],
            "Already on ANT?": [
                "Resolution already uploaded: link/torrentid=1",  # Pre 1.7.0, will be re-searched post 1.7.0
                "NOT FOUND",
                np.nan,
                np.nan,
                "Duplicate: exact filename already exists: test_link",
                "Partial duplicate: test_link",
                "x is banned from ANT - do no not upload",
            ],
        }
    )

    fs = FilmSearcher(test_df, "test_api_key")
    actual_df = fs.check_if_films_exist_on_ant()
    expected_df = pd.DataFrame(
        {
            "Full file path": [
                "C:/Movies/An awesome test film 1080p H264 Web-DL (2020).mkv",
                "C:/Movies/Another film (2020)/Another film (2020).mkv",
                "C:/Movies/Batman Begins 2160p H265 Blu-ray (2005).mkv",
                "C:/Movies/New film (2020)/New film (2020).mkv",
                "C:/Movies/Test (2020)/Test (2020).mkv",
                "C:/Movies/Test film (2020)/Test film (2020).mkv",
                "C:/Movies/zebras",
            ],
            "Film size (GB)": [2.0, 1.22, 5.0, 1.44, 1.11, 1.33,1.0],
            "Parsed film title": [
                "An awesome test film",
                "Another film",
                "Batman Begins",
                "New film",
                "Test",
                "test film",
                "zebras",
            ],
            "Resolution": ["1080p", "1080p", "2160p", "1080p", "1080p", "1080p", ""],
            "Codec": ["H264", "H264", "H265", "H264", "H264", "H264", ""],
            "Source": ["Web", "Blu-ray", "Blu-ray", "Web", "Blu-ray", "Blu-ray", ""],
            "Already on ANT?": [
                "Duplicate: exact filename already exists: test_link",
                "NOT FOUND",
                "Partial duplicate: test_link",
                np.nan,
                "Resolution already uploaded: link/torrentid=1",
                np.nan,
                "x is banned from ANT - do no not upload",
            ],
            "Should skip": [True, False, True, False, False, False, True],
            "API response": [[], [], [], [], [], [], []],
        }
    )

    assert (
        "Skipping 3 films already found on ANT in the previous output file..."
        in caplog.text
    )
    pd.testing.assert_frame_equal(actual_df, expected_df)


@pytest.mark.parametrize("film_title", ["A film", "A film with and in the title"])
def test_check_if_film_exists_on_ant_false(
    return_mock_search_for_film_on_ant_not_found, caplog, film_title
):
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.check_if_film_exists_on_ant(film_title)

    assert f"Searching for {film_title}" in caplog.text
    assert actual_return == []
    assert "--- Not found on ANT ---" in caplog.text

    if "and" in film_title:
        assert "Searching for A film with & in the title as well" in caplog.text


@pytest.mark.parametrize("film_title", ["A film"])
def test_check_if_film_exists_on_ant_true(
    return_mock_search_for_film_on_ant_torrentid, caplog, film_title
):
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.check_if_film_exists_on_ant(film_title)

    assert f"Searching for {film_title}" in caplog.text
    assert actual_return == [{"guid": "url/torrentid=1"}]
    assert "--- Not found on ANT ---" not in caplog.text


def test_replace_word_and_re_search(
    return_mock_search_for_film_on_ant_not_found, caplog
):
    caplog.set_level(logging.INFO)
    fs = FilmSearcher("test", "test_api_key")

    test_film = "Test film biscuit"
    test_regex = "biscuit"
    test_replacement = "jaffa"

    actual_return = fs.replace_word_and_re_search(
        test_film, test_regex, test_replacement
    )

    assert actual_return == []
    assert "Searching for Test film jaffa as well..." in caplog.text


films_four_numbers = {
    "1208 East of Bucharest": "Searching for 12:08 East of Bucharest as well...",
    "Test film 1508": "Searching for Test film 15:08 as well...",
    "Film 1000 test": "Searching for Film 10:00 test as well...",
}


@pytest.mark.parametrize("test_film", films_four_numbers)
def test_search_for_film_if_contains_potential_time_true(
    return_mock_search_for_film_on_ant_not_found, caplog, test_film
):
    caplog.set_level(logging.INFO)
    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_potential_date_or_time(
        test_film, format="time"
    )

    assert actual_return == []
    expected_log_info = films_four_numbers[test_film]
    assert expected_log_info in caplog.text
    assert "Film title may contain a date or time" in caplog.text


films_five_numbers = ["12345 test film", "Test film 12345", "Film 12345 test"]


@pytest.mark.parametrize("test_film", films_five_numbers)
def test_search_for_film_if_contains_potential_time_false(
    return_mock_search_for_film_on_ant_torrentid, caplog, test_film
):
    # Film search mock return is the torrentid. This should never be returned
    # If the film does not contain 4 numbers, as the search is skipped.
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_potential_date_or_time(
        test_film, format="time"
    )

    assert actual_return == []
    assert "Film title may contain a date or time" not in caplog.text


films_with_dates_numbers = {
    "77 One Day in London": "Searching for 7/7 One Day in London as well...",
    "Test film 11": "Searching for Test film 1/1 as well...",
    "Film 89 test": "Searching for Film 8/9 test as well...",
    "911 film": "Searching for 9/11 film as well...",
    "Fahrenheit 911": "Searching for Fahrenheit 9/11 as well...",
    "Film 112 test": "Searching for Film 1/12 test as well...",
}


@pytest.mark.parametrize("test_film", films_with_dates_numbers)
def test_search_for_film_if_contains_potential_date_true(
    return_mock_search_for_film_on_ant_not_found, caplog, test_film
):
    caplog.set_level(logging.INFO)
    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_potential_date_or_time(
        test_film, format="date"
    )

    assert actual_return == []
    expected_log_info = films_with_dates_numbers[test_film]
    assert expected_log_info in caplog.text
    assert "Film title may contain a date or time" in caplog.text


films_with_numbers_not_dates = [
    "7777 One Day in London",
    "Test film 1112",
    "Film 8910 test",
    "9 film",
    "Fahrenheit 91144",
    "Film 112444 test",
]


@pytest.mark.parametrize("test_film", films_five_numbers)
def test_search_for_film_if_contains_potential_date_false(
    return_mock_search_for_film_on_ant_torrentid, caplog, test_film
):
    # Film search mock return is the torrentid. This should never be returned
    # If the film does not contain 4 numbers, as the search is skipped.
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_potential_date_or_time(
        test_film, format="date"
    )

    assert actual_return == []
    assert "Film title may contain a date or time" not in caplog.text


films_with_alternate_titles = {
    "Alphaville une etrange aventure de Lemmy Caution AKA Alphaville": (
        "Alphaville une etrange aventure de Lemmy Caution",
        "Alphaville",
    ),
    "Title 1 aka Title 2": ("Title 1", "Title 2"),
}


@pytest.mark.parametrize("test_film", films_with_alternate_titles)
def test_search_for_film_if_contains_aka_true(
    return_mock_search_for_film_on_ant_not_found, caplog, test_film
):
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.search_for_film_if_contains_aka(test_film)

    assert actual_return == []
    assert "Film title may contain an alternate title" in caplog.text
    assert (
        f"Searching for {films_with_alternate_titles[test_film][0]} as well..."
        in caplog.text
    )
    assert (
        f"Searching for {films_with_alternate_titles[test_film][1]} as well..."
        in caplog.text
    )


films_with_no_alternate_title = [
    "Aka Test film",
    "Test film aka",
    "Film with baka in it",
]


@pytest.mark.parametrize("test_film", films_with_no_alternate_title)
def test_search_for_film_if_contains_aka_false(
    return_mock_search_for_film_on_ant_not_found, caplog, test_film
):
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.search_for_film_if_contains_aka(test_film)

    assert actual_return == []
    assert "Film title may contain an alternate title" not in caplog.text
    assert f"Searching for Test film as well" not in caplog.text
