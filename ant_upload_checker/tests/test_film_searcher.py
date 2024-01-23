import pandas as pd
import numpy as np
import pytest
import logging
from ant_upload_checker.film_searcher import FilmSearcher

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def return_mock_search_for_film_on_ant_not_found(monkeypatch):
    def mockreturn(test_arg, test_arg_2):
        return "NOT FOUND"

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
    assert actual_return == "NOT FOUND"
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

    assert actual_return == "NOT FOUND"
    assert "Searching for Test film jaffa as well..." in caplog.text


films_four_numbers = {
    "1208 East of Bucharest": "Searching for 12:08 East of Bucharest as well...",
    "Test film 1508": "Searching for Test film 15:08 as well...",
    "Film 1000 test": "Searching for Film 10:00 test as well...",
}


@pytest.mark.parametrize("test_film", films_four_numbers)
def test_search_for_film_if_contains_four_numbers_true(
    return_mock_search_for_film_on_ant_not_found, caplog, test_film
):
    caplog.set_level(logging.INFO)
    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_four_numbers(test_film)

    assert actual_return == "NOT FOUND"
    expected_log_info = films_four_numbers[test_film]
    assert expected_log_info in caplog.text


films_five_numbers = ["12345 test film", "Test film 12345", "Film 12345 test"]


@pytest.mark.parametrize("test_film", films_five_numbers)
def test_search_for_film_if_contains_four_numbers_false(
    return_mock_search_for_film_on_ant_torrentid, caplog, test_film
):
    # Film search mock return is the torrentid. This should never be returned
    # If the film does not contain 4 numbers, as the search is skipped.
    caplog.set_level(logging.INFO)

    fs = FilmSearcher("test", "test_api_key")

    actual_return = fs.search_for_film_if_contains_four_numbers(test_film)

    assert actual_return == "NOT FOUND"
    assert "Film contains 4 numbers" not in caplog.text
