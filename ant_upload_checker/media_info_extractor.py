from pathlib import Path
import logging
import time
from typing import Any, Optional, Callable
from pymediainfo import MediaInfo

from ant_upload_checker import utils


class MediaInfoExtractor:
    def __init__(self, file_paths: list[Path]):
        self.file_paths: list[Path] = file_paths
        self.films: list[MediaInfo] = []
        self.convert_paths_to_media_info()

    def convert_paths_to_media_info(self) -> list[MediaInfo]:
        start_time = time.time()
        self.films = [MediaInfo.parse(file_path) for file_path in self.file_paths]

        logging.info(f"Time: {time.time() - start_time}")

        return self.films

    def get_track_metadata(
        self,
        film: MediaInfo,
        track_type: str,
        metadata_to_extract: str,
        processing_function: Optional[Callable] = None,
    ):

        tracks = getattr(film, f"{track_type}_tracks", None)
        if tracks:
            for track in tracks:
                metadata = getattr(track, metadata_to_extract, None)
                if metadata:
                    if processing_function:
                        return processing_function(metadata)
                    else:
                        return metadata

        return None

    def get_runtime(self, film: MediaInfo) -> Optional[int]:
        runtime = self.get_track_metadata(
            film,
            track_type="general",
            metadata_to_extract="duration",
            processing_function=utils.convert_milliseconds_to_minutes,
        )

        return runtime

    def get_size_in_gb(self, film: MediaInfo) -> Optional[str]:
        size_in_gb = self.get_track_metadata(
            film,
            track_type="general",
            metadata_to_extract="file_size",
            processing_function=utils.convert_bytes_to_gb,
        )
        return size_in_gb

    def get_resolution(self, film: MediaInfo) -> Optional[str]:
        resolution = self.get_track_metadata(
            film,
            track_type="video",
            metadata_to_extract="width",
            processing_function=utils.convert_width_to_resolution,
        )

        return resolution

    def get_codec(self, film: MediaInfo) -> Optional[str]:
        codec = self.get_track_metadata(
            film,
            track_type="video",
            metadata_to_extract="format",
            processing_function=utils.convert_video_codec_format,
        )

        return codec

    def extract_metadata_from_media_info(self) -> dict[str, list[Any]]:
        metadata = {}
        metadata_functions = {
            "file_size": self.get_size_in_gb,
            "resolution": self.get_resolution,
            "runtime": self.get_runtime,
            "codec": self.get_codec,
        }

        for metadata_name, function in metadata_functions.items():
            metadata[metadata_name] = [function(film) for film in self.films]

        return metadata
