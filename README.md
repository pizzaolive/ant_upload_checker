# ANT upload checker

# What does this script do?
This script is intended to be used on a directory containing films. It scans for films, parses their film titles and checks whether each film already exists on ANT. The script outputs a csv file containing the film list along with info on whether it's been uploaded or not. The idea is to help find films in your library that could potentially be uploaded.

Example CSV output:

| Full file path                                             | Film size (GB) | Parsed film title | Already on ANT? |
|------------------------------------------------------------|----------------|-------------------|-----------------|
| C:\Movies\Asteroid City (2023)\Asteroid.City.2023.1080.mkv | 10.62          | Asteroid City     | url       |
| C:\Movies\A made up film (2023)\A made up film (2023).mp4  | 5.14           | A made up film    | NOT FOUND       |


## How does it work?

This script is intended to be used on a directory containing films. It searches through the given directory and sub-directories, and finds them by searching for common video file formats (currently: mp4, avi, mkv, mpeg and m2ts). Using an existing package called guessit and some additional tweaks, film titles are parsed from the file paths.

The script outputs a csv file containing a list of films it's found, with the link to the ANT torrent if it already exists, or "NOT FOUND" if not.

As of version 1.4, if an existing film_list.csv is found in the output location specified, any films in this that have already been found on ANT will be skipped by the process. This means you can re-run the script without having to search through your whole film library again. It will not skip films that were not found on ANT, and any new films in your library.

This is a work in progress - please feel free to give helpful feedback and report bugs.

## Known issues
* Non-english films may not be found on ANT if their titles do not match
* Films with ellipsis may not be found. Currently guessit automatically removes these e.g. Tick Tick... BOOM! -> Tick Tick Boom!
* Films with alternate titles (Film X AKA Film Y) will not be found on ANT
* Film titles that should contain symbols like "/" or ":" but don't in their file names aren't found on ANT


## Prerequisites
* You must have Python installed: https://www.python.org/downloads/windows/
* You must be a member of ANT
    * Please do not message me for an invite, or open issues requesting one, these will be ignored. ANT Staff is aware of and monitors this repo

## Setting up the script

1. Git clone the respository, or download it as ZIP (click the green Code button -> Download ZIP) and extract it to wherever you like.
2. Update the values in [parameters.py](ant_upload_checker\parameters.py). You can right click the file and open with Notepad to edit it.
    * API_KEY: Your API key from ANT. Go to the tracker to find out how to get this.
    * INPUT_FOLDERS: the parent directory or multiple different directories that contain your films.
    * OUTPUT_FOLDER: the directory in which the output csv file containing the list of films should go.

## Running the script
1. Navigate into the root folder. You should be able to see the README and setup files.
2. Open the terminal in the current folder. You can do this by clicking the directory bar at the top, typing in 'cmd', and pressing Enter.
3. Type `pip install .` into the terminal and press Enter - this should use setup.py and install the packages required (pandas, requests, ratelimit, pytest).
4. Once the packages have finished installing, type `python -m ant_upload_checker.main` and press Enter.
    * You should see some information being printed in the terminal, including a message once it's finished running.
5. Open the output csv file to see which films already exist on the tracker


## Future versions
### Version 4.3.2
- [] https://github.com/pizzaolive/ant_upload_checker/issues/5 

## Future ideas
* Add ability to exclude TV shows if some are found within directory
* Use enquirer or GUI to select folder paths?
* Automatic torrent creation?
* Look into auto-upload missing torrents?
