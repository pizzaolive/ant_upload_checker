# ANT upload checker

## What does this script do?
This script is intended to be used on a directory containing films. It scans for films, parses their title and resolution, and checks whether a given film and its resolution already exists on ANT. The script outputs a csv file containing the film list along with information on whether it's been uploaded or not. The idea is to help find films in your library that could potentially be uploaded.

Example CSV output:

| Full file path                                                  | Parsed film title | Film size (GB) | Resolution | Already on ANT?                                                     |
|-----------------------------------------------------------------|-------------------|----------------|------------|---------------------------------------------------------------------|
| C:\Movies\Asteroid City (2023)\Asteroid.City.2023.1080p.mkv     | Asteroid City     | 10.62          | 1080p      | Resolution already uploaded: (link to film)                         |
| C:\Movies\Cold War (2018)\Cold.War.2018.mkv                     | Cold War          | 5.01           |            | On ANT, but could not get resolution from file name: (link to film) |
| C:\Movies\A made up film (2023)\A made up film (2023) 2160p.mp4 | A made up film    | 5.14           | 2160p      | NOT FOUND                                                           |




## :grey_question: How does it work?

The process searches through the given directory (or multiple directories), and finds all common video file formats (currently: mp4, avi, mkv, mpeg and m2ts). Using an existing package called [guessit](https://github.com/guessit-io/guessit) and some additional processing, film titles and their resolutions are parsed from the file paths. For each film, a get request is sent to ANT's API, to check whether it can be found already. For certain titles, if an initial match is not found, the title is tweaked and re-searched. For example, films containing "and" could be spelt with "and" or "&", so both titles are checked.

The script outputs a csv file containing a list of films it's found and whether they've been found on ANT or not.

If an existing film_list.csv is found in the output location specified, any films in this that have already been found on ANT will be skipped by the process. This means you can re-run the script without having to search through your whole film library again. It will not skip films that were not found on ANT, and any new films in your library.

This is a work in progress - please feel free to give helpful feedback and report bugs.

## :grey_exclamation: Known issues
* Non-english films may not be found on ANT if their titles do not match
* Films with ellipsis may not be found. Currently guessit automatically removes these e.g. Tick Tick... BOOM! -> Tick Tick Boom!
* Films with alternate titles (Film X AKA Film Y) will not be found on ANT

## :clipboard: Prerequisites
* You must have Python v 3.8 or later installed: https://www.python.org/downloads/windows/
* You must be a member of ANT
    * Please do not message me for an invite, or open issues requesting one, these will be ignored. ANT Staff is aware of and monitors this repo

## :page_with_curl: Setting up the script

1. Git clone the respository, or download it as ZIP (click the green Code button -> Download ZIP) and extract it to wherever you like.
2. Update the values in [parameters.py](ant_upload_checker\parameters.py). You can right click the file and open with Notepad to edit it.
    * API_KEY: Your API key from ANT. Go to the tracker to find out how to get this.
    * INPUT_FOLDERS: the parent directory or multiple different directories that contain your films.
    * OUTPUT_FOLDER: the directory in which the output csv file containing the list of films should go.

## :page_with_curl: Running the script
1. Navigate into the root folder. You should be able to see the README and setup files.
2. Open the terminal in the current folder. You can do this by clicking the directory bar at the top, typing in 'cmd', and pressing Enter.
3. Type `pip install .` into the terminal and press Enter - this should automatically install the dependencies needed.
4. Once the packages have finished installing, type `python -m ant_upload_checker.main` and press Enter.
    * You should see information being printed in the terminal as the process runs
5. Open the output csv file to see which films already exist on the tracker


## :rainbow: Future versions
### Version 1.4.5
- [ ] Add automatic torrent creator using Torf

#### Recent versions
#### Version 1.4.4
- [x] Look into fix for films with alternate titles (x AKA y)

##### Version 1.4.3
- [x] Add resolution dupe check https://github.com/pizzaolive/ant_upload_checker/issues/16. Process will check if the specific resolution of your films are on ANT already or not.

##### Version 1.4.2
- [x] Fix for films that should contain "/" or ":" within times or dates in tiles https://github.com/pizzaolive/ant_upload_checker/issues/5 


## :bulb: Future ideas 
* Look into using tmdb or imdb to match films first, if that fails, rely on title
* Add ability to exclude TV shows if some are found within directory
* Use enquirer or GUI to select folder paths


