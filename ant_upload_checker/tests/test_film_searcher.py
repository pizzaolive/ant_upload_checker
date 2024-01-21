import pandas as pd
from ant_upload_checker.film_searcher import FilmSearcher


# def test_check_if_films_exist_on_ant():
#     test_df = pd.DataFrame(
#         {
#             "Full file path": [
#                 "C:/Movies/Test (2020)/Test (2020).mkv",
#                 "C:/Movies/Another film (2020)/Another film (2020).mkv",
#                 "C:/Movies/Test film (2020)/Test film (2020).mkv",
#                 "C:/Movies/New film (2020)/New film (2020).mkv",
#             ],
#             "Film size (GB)": [1.11, 1.22, 1.33, 1.44],
#             "Parsed film title": ["Test", "Another film", "test film", "New film"],
#             "Already on ANT?": ["link/torrentid=1", "NOT FOUND", np.nan, np.nan],
#         }
#     )

#     fs = FilmSearcher(test_df, "test_api_key")
