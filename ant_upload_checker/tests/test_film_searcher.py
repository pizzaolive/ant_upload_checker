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
                r"C:\Media\Films\Desert.Flower.2009.1080p.BluRay.x264.DTS-WiKi.mkv",
                r"C:\Media\Films\Dogville (2003) [imdbid-tt0276919] - [Bluray-1080p][DTS-HD MA 5.1][x265]-TAoE.mkv",
                r"C:\Media\Films\Aftersun (2022).mkv",
                r"C:\Media\Films\American Graffiti (1973) [imdbid-tt0069704] - [Remux-1080p Proper][FLAC 2.0][VC1]-KRaLiMaRKo.mkv",
                r"C:\Media\Films\A Man Called Otto (2022) [imdbid-tt7405458] - [Bluray-1080p][EAC3 5.1][x264]-playHD.mkv",
                r"C:\Media\Films\The Last Black Man in San Francisco (2019) [imdbid-tt4353250] - [Bluray-1080p][DTS-HD MA 5.1][x265]-CHD.mkv",
            ],
            "Parsed film title": [
                "Desert Flower",
                "Dogville",
                "Aftersun",
                "American Graffiti",
                "A Man Called Otto",
                "The Last Black Man in San Francisco",
            ],
            "Film size (GB)": [
                18.71,
                11.06,
                17.12,
                26.35,
                16.83,
                6.34,
            ],
            "Resolution": [
                "1080p",
                "1080p",
                "",
                "1080p",
                "1080p",
                "1080p",
            ],
            "Codec": ["H264", "H265", "", "VC-1", "H264", "H265"],
            "Source": ["Blu-ray", "Blu-ray", "", "", "Blu-ray", "Blu-ray"],
            "Release group": ["wiki", "taoe", "", "kralimark", "playhd", "chd"],
            "Already on ANT?": [
                "Uploadable - potentially",
                "Uploadable",
                "Duplicate - potentially",
                "Duplicate - partial",
                "Duplicate",
                "Banned",
            ],
            "Info": [
                "Film not found on ANT - does not already exist, or title failed to match",
                "A film with 1080p/H265/Blu-ray does not already exist. test_link",
                "On ANT, but could not dupe check (could not extract resolution/codec/media from filename). test_link",
                "A film with 1080p/VC-1 already exists. Could not extract and check media from filename. test_link",
                "A film with 1080p/H264/Blu-ray already exists: test_link",
                "Release group 'chd' is banned from ANT - do not upload",
            ],
        }
    )

    fs = FilmSearcher(test_df, "test_api_key")
    actual_df = fs.check_if_films_exist_on_ant()
    expected_df = pd.DataFrame(
        {
            "Full file path": [
                r"C:\Media\Films\A Man Called Otto (2022) [imdbid-tt7405458] - [Bluray-1080p][EAC3 5.1][x264]-playHD.mkv",
                r"C:\Media\Films\Aftersun (2022).mkv",
                r"C:\Media\Films\American Graffiti (1973) [imdbid-tt0069704] - [Remux-1080p Proper][FLAC 2.0][VC1]-KRaLiMaRKo.mkv",
                r"C:\Media\Films\Desert.Flower.2009.1080p.BluRay.x264.DTS-WiKi.mkv",
                r"C:\Media\Films\Dogville (2003) [imdbid-tt0276919] - [Bluray-1080p][DTS-HD MA 5.1][x265]-TAoE.mkv",
                r"C:\Media\Films\The Last Black Man in San Francisco (2019) [imdbid-tt4353250] - [Bluray-1080p][DTS-HD MA 5.1][x265]-CHD.mkv",
            ],
            "Parsed film title": [
                "A Man Called Otto",
                "Aftersun",
                "American Graffiti",
                "Desert Flower",
                "Dogville",
                "The Last Black Man in San Francisco",
            ],
            "Film size (GB)": [
                16.83,
                17.12,
                26.35,
                18.71,
                11.06,
                6.34,
            ],
            "Resolution": [
                "1080p",
                "",
                "1080p",
                "1080p",
                "1080p",
                "1080p",
            ],
            "Codec": ["H264", "", "VC-1", "H264", "H265", "H265"],
            "Source": ["Blu-ray", "", "", "Blu-ray", "Blu-ray", "Blu-ray"],
            "Release group": ["playhd", "", "kralimark", "wiki", "taoe", "chd"],
            "Already on ANT?": [
                "Duplicate",
                "Duplicate - potentially",
                "Duplicate - partial",
                "Uploadable - potentially",
                "Uploadable",
                "Banned",
            ],
            "Info": [
                "A film with 1080p/H264/Blu-ray already exists: test_link",
                "On ANT, but could not dupe check (could not extract resolution/codec/media from filename). test_link",
                "A film with 1080p/VC-1 already exists. Could not extract and check media from filename. test_link",
                "Film not found on ANT - does not already exist, or title failed to match",
                "A film with 1080p/H265/Blu-ray does not already exist. test_link",
                "Release group 'chd' is banned from ANT - do not upload",
            ],
            "Should skip": [True, True, True, False, False, True],
            "API response": [[], [], [], [], [], []],
        }
    )

    assert (
        "Skipping 4 films already found on ANT in the previous output file..."
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
