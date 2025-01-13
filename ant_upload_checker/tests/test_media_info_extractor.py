import pytest
from ant_upload_checker.media_info_extractor import MediaInfoExtractor
from pymediainfo import MediaInfo


@pytest.fixture
def mock_media_info(monkeypatch):
    class MockTrack:
        def __init__(
            self,
            width=None,
            format=None,
            duration=None,
            file_size=None,
        ):
            self.width = width
            self.format = format
            self.duration = duration
            self.file_size = file_size

    class MockMediaInfo:
        def __init__(self):
            self.video_tracks = [MockTrack(width=1920, format="AVC")]
            self.general_tracks = [MockTrack(file_size=8053063680, duration=7200000)]

    def mock_parse(file_path):
        return MockMediaInfo()

    monkeypatch.setattr(MediaInfo, "parse", mock_parse)


def test_get_track_metadata(mock_media_info):
    media_extractor = MediaInfoExtractor(["test.mp4"])
    duration = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="general",
        metadata_to_extract="duration",
        processing_function=None,
    )
    assert duration == 7200000

    duration_with_processing = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="general",
        metadata_to_extract="duration",
        processing_function=lambda x: x / 2,
    )
    assert duration_with_processing == 3600000

    format = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="video",
        metadata_to_extract="format",
        processing_function=None,
    )
    assert format == "AVC"

    file_size = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="general",
        metadata_to_extract="file_size",
        processing_function=None,
    )
    assert file_size == 8053063680

    width = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="video",
        metadata_to_extract="width",
        processing_function=None,
    )
    assert width == 1920


# TODO : make mock class more flexible, add test cases to
# test all possible resolutions, codecs


def test_get_size_in_gb(mock_media_info):
    media_extractor = MediaInfoExtractor(["test.mp4"])
    size_in_gb = media_extractor.get_size_in_gb(media_extractor.films[0])

    assert size_in_gb == 7.5


def test_get_resolution(mock_media_info):
    media_extractor = MediaInfoExtractor(["test.mp4"])
    resolution = media_extractor.get_resolution(media_extractor.films[0])

    assert resolution == "1080p"


def test_get_runtime(mock_media_info):
    media_extractor = MediaInfoExtractor(["test.mp4"])
    runtime = media_extractor.get_runtime(media_extractor.films[0])

    assert runtime == 120


def test_get_codec(mock_media_info):
    media_extractor = MediaInfoExtractor(["test.mp4"])
    codec = media_extractor.get_codec(media_extractor.films[0])

    assert codec == "H264"
