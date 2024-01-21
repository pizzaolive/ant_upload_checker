import pandas as pd
import numpy as np
import pytest
import logging
from ant_upload_checker.film_searcher import FilmSearcher

LOGGER = logging.getLogger(__name__)


def test_check_if_films_exist_on_ant(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def mockreturn(test_arg, test_arg_2):
        return "NOT FOUND"

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.check_if_film_exists_on_ant", mockreturn
    )

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
def test_check_if_film_exists_on_ant_false(monkeypatch, caplog, film_title):
    caplog.set_level(logging.INFO)

    def mockreturn(test_arg, test_arg_2):
        return "NOT FOUND"

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.check_if_film_exists_on_ant(film_title)

    assert f"Searching for {film_title}" in caplog.text
    assert actual_return == "NOT FOUND"
    assert "--- Not found on ANT ---" in caplog.text

    if "and" in film_title:
        assert (
            "Searching for A film with & in the title as well, just in case..."
            in caplog.text
        )


@pytest.mark.parametrize("film_title", ["A film"])
def test_check_if_film_exists_on_ant_true(monkeypatch, caplog, film_title):
    caplog.set_level(logging.INFO)

    def mockreturn(test_arg, test_arg_2):
        return "url/torrentid=1"

    monkeypatch.setattr(
        "test_film_searcher.FilmSearcher.search_for_film_title_on_ant", mockreturn
    )

    fs = FilmSearcher("test", "test_api_key")
    actual_return = fs.check_if_film_exists_on_ant(film_title)

    assert f"Searching for {film_title}" in caplog.text
    assert actual_return == "url/torrentid=1"
    assert "--- Not found on ANT ---" not in caplog.text
