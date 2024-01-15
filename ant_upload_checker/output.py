from ant_upload_checker.parameters import OUTPUT_FOLDER
import logging


def write_film_list_to_csv(output_df):
    if not output_df.empty:
        output_file_path = OUTPUT_FOLDER + "\Film list.csv"
        logging.info(f"Writing list of films to {output_file_path} ...")
        output_df.to_csv(output_file_path, index=False, encoding="utf-8-sig")
    else:
        logging.warning("The film list is empty, no file is being created.")