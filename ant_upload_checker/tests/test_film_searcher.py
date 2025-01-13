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
