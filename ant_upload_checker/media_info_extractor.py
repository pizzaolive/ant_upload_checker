from pathlib import Path
import logging
import time
from typing import Any, Optional
from pymediainfo import MediaInfo

from ant_upload_checker import utils


# TODO refactor filmprocesser, move extraction of properties to here
class MediaInfoExtractor:
    def __init__(self, file_paths: list[Path]):
        self.file_paths: list[Path] = file_paths
        self.films: list[MediaInfo] = []

    def convert_paths_to_media_info(self):
        logging.info("Extracting media info from files...")
        start_time = time.time()
        self.films = [MediaInfo.parse(file_path) for file_path in self.file_paths]
        logging.info(f"Time: {time.time() - start_time}")

        return self.films

    def get_film_runtime(self, film: MediaInfo) -> Optional[int]:
        for track in film.general_tracks:
            if track.duration:
                runtime_minutes = round(track.duration / 60000)
                return runtime_minutes

        return None

    def get_film_size(self, film: MediaInfo) -> Optional[str]:
        for track in film.general_tracks:
            if track.file_size:
                file_size_gb = utils.convert_bytes_to_gb(track.file_size)
                return file_size_gb

        return None

    def get_film_resolution(self, film: MediaInfo) -> Optional[str]:
        resolution_map = {3840: "2160p", 1920: "1080p", 1280: "720p", 720: "480p"}

        for track in film.video_tracks:
            if track.width:
                resolution = resolution_map.get(track.width, None)
                return resolution

        return None

    def extract_metadata_from_media_info(self) -> dict[str, list[Any]]:
        metadata = {}
        metadata_functions = {
            "file_size": self.get_film_size,
            "resolution": self.get_film_resolution,
            "runtime": self.get_film_runtime,
        }

        for metadata_name, function in metadata_functions.items():
            metadata[metadata_name] = [function(film) for film in self.films]

        return metadata
