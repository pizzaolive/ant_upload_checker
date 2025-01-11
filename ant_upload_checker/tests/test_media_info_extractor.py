import pytest
from ant_upload_checker.media_info_extractor import MediaInfoExtractor
from pymediainfo import MediaInfo


@pytest.fixture
def mock_media_info(monkeypatch):
    class MockTrack:
        def __init__(
            self,
            width=None,
            runtime=None,
            format=None,
            duration=None,
            file_size=None,
        ):
            self.width = width
            self.runtime = runtime
            self.format = format
            self.duration = duration
            self.file_size = file_size

    class MockMediaInfo:
        def __init__(self):
            self.video_tracks = [MockTrack(width=720, runtime=20000, format="AVC")]
            self.general_tracks = [MockTrack(file_size=100000, duration=20000)]

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
    assert duration == 20000

    duration_with_processing = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="general",
        metadata_to_extract="duration",
        processing_function=lambda x: x / 2,
    )
    assert duration_with_processing == 10000

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
    assert file_size == 100000

    width = media_extractor.get_track_metadata(
        media_extractor.films[0],
        track_type="video",
        metadata_to_extract="width",
        processing_function=None,
    )
    assert width == 720
