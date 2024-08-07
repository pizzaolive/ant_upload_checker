from pathlib import Path
import logging
import pandas as pd


def write_film_list_to_csv(output_df: pd.DataFrame, output_folder: Path) -> None:
    if not output_df.empty:
        output_file_path = Path(output_folder).joinpath("Film list.csv")

        parent_directory = output_file_path.parents[0]
        if not parent_directory.is_dir():
            logging.info(
                "\nOutput directory '%s' not found but has been created",
                parent_directory,
            )
            parent_directory.mkdir(parents=True, exist_ok=True)

        logging.info("Writing list of films to %s...", output_file_path)

        output_df.to_csv(output_file_path, index=False, encoding="utf-8-sig")
    else:
        logging.warning("\nThe film list is empty, no file is being created.")
