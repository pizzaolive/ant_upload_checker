# ANT upload checker

## What does this script do?
This script is intended to be used on a directory containing films. It scans for films, parses their title and resolution, and checks whether a given film and its resolution already exists on ANT. The script outputs a csv file containing the film list along with information on whether it's been uploaded or not. The idea is to help find films in your library that could potentially be uploaded.

Example CSV output:

| Full file path                                                                                                                     | Parsed film title  | Film size (GB) | Resolution | Codec | Source  | Release group | Already on ANT?                   |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------------------ | -------------- | ---------- | ----- | ------- | ------------- | --------------------------------- |
| C:\Movies\25th Hour 2002 1080p BluRay DTS x264-GrapeHD.mkv                                                     | 25th Hour          | 18.9           | 1080p      | H.264 | Blu-ray | GrapeHD       | Resolution already uploaded: link |
| C:\Movies\A Clockwork Orange (1971) [imdbid-tt0066921] - [Bluray-1080p][HDR10][Opus 1.0][x265]-ZQ.mkv | A Clockwork Orange | 23.21          | 1080p      | H.265 | Blu-ray | ZQ            | Resolution already uploaded: link |
| C:\Movies\A Man Called Otto (2022) [imdbid-tt7405458] - [Bluray-1080p][EAC3 5.1][x264]-playHD.mkv      | A Man Called Otto  | 16.83          | 1080p      | H.264 | Blu-ray | playHD        | Resolution already uploaded: link |
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

## :page_with_curl: Running the script
1. Navigate into the root folder. You should be able to see the README and setup files.
2. Open a terminal in the current folder. You can do this by clicking the directory bar at the top, typing in 'cmd', and pressing Enter.
3. Type `pip install .` into the terminal and press Enter - this should automatically install the dependencies needed.
4. Once the packages have finished installing, type `python -m ant_upload_checker.main` and press Enter.
    * You should be asked for your ANT API key - you can paste this in after copying it from ANT
    * A dialog box should then open asking for your input folders (where your films are stored)
    * Finally, another dialog box should ask you to specify your output folder (where the film list CSV should be written)
    * When you run it for a second time, you can skip this stage by selecting "No" when asked whether you want to overwrite your existing settings
5. Open the output csv file to see which films already exist on the tracker


## :rainbow: Future versions
#### Version 1.4.9
- [ ] Enhance film check to include other attributes (codec, source info etc.)
- [ ] Continue code refactor, finish adding type hints

#### Recent versions
### Version 1.4.8.1
= [x] Patch to address dependabot warnings in dev requirements

#### Version 1.4.8
- [x] Add GUI for user to input API key and folder paths on initial setup
- [x] Code refactor including adding type hints

#### Version 1.4.7
- [x] Attempt bug fix for [#24](https://github.com/pizzaolive/ant_upload_checker/issues/24)

#### Version 1.4.6
- [x] Bug fix for [#21](https://github.com/pizzaolive/ant_upload_checker/issues/21)
- [x] Fix parent directory displaying warning even if directory exists

#### Version 1.4.5
- [x] Add additional film info (codec and source), output directory is now automatically created if it does not exist

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


