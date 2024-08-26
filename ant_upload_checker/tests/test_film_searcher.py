import pandas as pd
import numpy as np
import pytest
import logging
from ant_upload_checker.film_searcher import FilmSearcher

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def return_mock_search_for_film_on_ant_not_found(monkeypatch):
    def mockreturn(test_arg, test_arg_2):
        return None

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )


@pytest.fixture
def return_mock_search_for_film_on_ant_torrentid(monkeypatch):
    def mockreturn(test_arg, test_arg_2):
        return "url/torrentid=1"

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )


def test_check_if_films_exist_on_ant(
    return_mock_search_for_film_on_ant_not_found, caplog
):
    caplog.set_level(logging.INFO)

    test_df = pd.DataFrame(
        {
            "Full file path": [
                "C:/Movies/Test (2020)/Test (2020).mkv",
                "C:/Movies/Another film (2020)/Another film (2020).mkv",
                "C:/Movies/Test film (2020)/Test film (2020).mkv",
                "C:/Movies/New film (2020)/New film (2020).mkv",
            ],
            "Film size (GB)": [1.11, 1.22, 1.33, 1.44],
            "Parsed film title": ["Test", "Another film", "test film", "New film"],
            "Resolution": ["1080p", "1080p", "1080p", "1080p"],
            "Already on ANT?": ["link/torrentid=1", "NOT FOUND", np.nan, np.nan],
        }
    )

    fs = FilmSearcher(test_df, "test_api_key")
    actual_df = fs.check_if_films_exist_on_ant()
    expected_df = pd.DataFrame(
        {
            "Full file path": [
                "C:/Movies/Another film (2020)/Another film (2020).mkv",
                "C:/Movies/New film (2020)/New film (2020).mkv",
                "C:/Movies/Test (2020)/Test (2020).mkv",
                "C:/Movies/Test film (2020)/Test film (2020).mkv",
            ],
            "Film size (GB)": [
                1.22,
                1.44,
                1.11,
                1.33,
            ],
            "Parsed film title": [
                "Another film",
                "New film",
                "Test",
                "test film",
            ],
            "Resolution": ["1080p", "1080p", "1080p", "1080p"],
            "Already on ANT?": [
                "NOT FOUND",
                "NOT FOUND",
                "link/torrentid=1",
                "NOT FOUND",
            ],
        }
    )

    assert (
        "Skipping 1 films already found on ANT in the previous output file..."
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
    assert actual_return == "url/torrentid=1"
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

    assert actual_return is None
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

    assert actual_return is None
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

    assert actual_return is None
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
        f"Searching for {films_with_alternate_titles[test_film][0]} as well"
        in caplog.text
    )
    assert (
        f"Searching for {films_with_alternate_titles[test_film][1]} as well"
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


test_resolution_values = [
    ("", [{"guid": "test_link"}]),
    ("", []),
]
expected_resolution_values = [
    "On ANT, but could not get resolution from file name: test_link",
    "On ANT, but could not get resolution from file name: (Failed to extract URL from API response)",
]


@pytest.mark.parametrize(
    ("test_input", "test_output"),
    zip(test_resolution_values, expected_resolution_values),
)
def test_check_if_film_resolution_exists_on_ant(test_input, test_output):
    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.check_if_resolution_exists_on_ant(test_input[0], test_input[1])

    assert actual_return == test_output


test_values = [
    ("file_path", "1080p", []),
    (
        "C:/films/test_film_name.mkv",
        "1080p",
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
        [
            {
                "guid": "test_link",
                "files": [
                    {"size": "1", "name": "unwanted_file.nfo"},
                    {"size": "100", "name": "test_film_name_2.mkv"},
                ],
            }
        ],
    ),
]
expected_values = [
    "NOT FOUND",
    "Exact filename already exists on ANT: test_link",
]


@pytest.mark.parametrize(
    ("test_input", "test_output"),
    zip(test_values, expected_values),
)
def test_check_if_film_is_duplicate(test_input, test_output):
    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.check_if_film_is_duplicate(
        test_input[0], test_input[1], test_input[2]
    )

    assert actual_return == test_output
