import logging
import requests
from pathlib import Path
from torf import Torrent
import ant_upload_checker.parameters as parameters


class FilmUploader:
    def __init__(self, film_list, api_key):
        self.film_list = film_list
        self.api_key = api_key
        self.banned_list = parameters.BANNED_GROUPS

    def check_if_group_is_banned(self):

        return None

    def create_all_torrent_files(self):
        torrents = self.film_list["Full file path"].apply(self.create_single_torrent)

        return torrents

    def upload_film():

        return None

    def provide_torrent_progress_info(
        self, torrent, file_path, pieces_done, pieces_total
    ):
        progress_info = f"-- {pieces_done/pieces_total*100:3.0f} % done"
        logging.info(progress_info)

    def create_single_torrent(self, file_path):
        file_path = Path(file_path)

        if file_path.is_file():
            logging.info("Generating torrent file for %s...", file_path)
            torrent = Torrent(
                file_path,
                trackers=[parameters.ANNOUNCE_URL],
                source="ANT",
                name=file_path.stem,
                private=True,
            )
            torrent.generate(callback=self.provide_torrent_progress_info, interval=5)

            output_path = Path(parameters.OUTPUT_FOLDER).joinpath(
                file_path.stem + ".torrent"
            )
            torrent.write(output_path, overwrite=True)

            logging.info("Finished generating file, saved at: %s", output_path)
        else:
            logging.info("File no longer found, skipping: %s", file_path)
