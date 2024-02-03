from ant_upload_checker.parameters import OUTPUT_FOLDER
from pathlib import Path
import logging


def write_film_list_to_csv(output_df):
    if not output_df.empty:
        output_file_path = Path(OUTPUT_FOLDER).joinpath("Film list.csv")
        logging.info("\nWriting list of films to %s...", output_file_path)
        output_df.to_csv(output_file_path, index=False, encoding="utf-8-sig")
    else:
        logging.warning("\nThe film list is empty, no file is being created.")
