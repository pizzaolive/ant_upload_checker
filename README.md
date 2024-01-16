# ANT upload checker

# What does this script do?
This script is intended to be used on a directory containing films. It scans for films, parses their film titles and checks whether each film already exists on ANT. The script outputs a csv file containing the film list along with info on whether it's been uploaded or not. The idea is to help find films in your library that could potentially be uploaded.

## How does it work?

This script is intended to be used on a directory containing films. It searches through the given directory and sub-directories, and finds MKV files. It converts the file names into films, assuming that the MKV files are in the format: "Film title (year)" or "Film.title.year". 

It should work on unedited file names from trackers, but there may still be edge cases where a film name isn't correctly extracted. It's worth checking that film names have been correctly parsed in the output.
* Note if non-english films are spelt differently to how they're named on Ant, a match will not be found

The script outputs a csv file containing a list of films it's found, with the link to the ANT torrent if it already exists, or "NOT FOUND" if not.

This is a work in progress - please feel free to give helpful feedback and report bugs.

## Prerequisites
* You must have Python installed: https://www.python.org/downloads/windows/
* You must be a member of ANT
    * Please do not message me for an invite, or open issues requesting one, these will be ignored. ANT Staff is aware of and monitors this repo

## Setting up the script

1. Git clone the respository, or download it as ZIP (click the green Code button -> Download ZIP) and extract it to wherever you like.
2. Update the values in [parameters.py](ant_upload_checker\parameters.py). You can right click the file and open with Notepad to edit it.
    * API_KEY: Your API key from ANT. Go to the tracker to find out how to get this.
    * INPUT_FOLDER: the parent directory that contains films.
    * OUTPUT_FOLDER: the directory in which the output csv file containing the list of films should go.

## Running the script
1. Navigate into the root folder. You should be able to see the README and setup files.
2. Open the terminal in the current folder. You can do this by clicking the directory bar at the top, typing in 'cmd', and pressing Enter.
3. Type `pip install .` into the terminal and press Enter - this should use setup.py and install the packages required (pandas, requests, ratelimit, pytest).
4. Once the packages have finished installing, type `python -m ant_upload_checker.main` and press Enter.
    * You should see some information being printed in the terminal, including a message once it's finished running.
5. Open the output csv file to see which films already exist on the tracker


## Future ideas
* Ensure regex works for unforseen edge cases
    * Look into guessit package
* Add tests
* Use enquirer or GUI to select folder paths?
* Automatic torrent creation
* Look into auto-upload missing torrents