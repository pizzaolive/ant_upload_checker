import logging
from typing import Any

from pathlib import Path
from pymediainfo import MediaInfo


# TODO refactor filmprocesser, move extraction of properties to here
class MediaInfoExtractor:
    def __init__(self, file_paths: list[Path]):
        self.file_paths: list[Path] = file_paths
        self.films: list[MediaInfo] = []

    def convert_paths_to_media_info(self):
        self.films = [MediaInfo.parse(file_path) for file_path in self.file_paths]

        return self.films

    def get_film_runtime(self, film: MediaInfo) -> int:
        for track in film.tracks:
            if track.track_type == "General":
                if track.duration:
                    runtime_minutes = round(track.duration / 60000)
                    return runtime_minutes

        return None

    def extract_metadata_from_media_info(self):
        film_runtimes = [self.get_film_runtime(film) for film in self.films]

        return film_runtimes
