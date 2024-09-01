# ANT upload checker

## What does this script do?
This script is intended to be used on a directory containing films. It scans for films, parses some film properties, and checks whether a given film is already on ANT, and whether it's a duplicate or not. A CSV file will be created by the process, containing your film list. The idea is to help find films in your library that could potentially be uploaded.

Currently the script checks if a film is a duplicate based on resolution, codec and source (AKA media). It also checks if the release group (only if extracted successfully) is on the banned list.

#### Example CSV output:
| Full file path                                                                   | Parsed film title  | Film size (GB) | Resolution | Codec | Source  | Release group         | Already on ANT?                                                                                                  |Info |
|----------------------------------------------------------------------------------|--------------------|----------------|------------|-------|---------|-----------------------|------------------------------------------------------------------------------------------------------------------|-|
| C:\Movies\Another great film (2002) 1080p H264 Blu-ray made_up_release_group.mkv | Another great film | 7.0            | 1080p      | H264  | Blu-ray | made_up_release_group | Uploadable - potentially        | Film does not exist, or could not match title|
| C:\Movies\A great film (2001) 1080p H264 Blu-ray made_up_release_group.mkv       | A great film       | 10.0           | 1080p      | H264  | Blu-ray | made_up_release_group | Uploadable                                    | A film with 1080p/H264/Web does not already exists. link               |
| C:\Movies\Film with no info.mkv                                                  | Film with no info  | 0.5            |            |       |         |                       | Duplicate - potentially               |         On ANT, but could not dupe check (could not extract resolution/codec/media from filename). test_link |
| C:\Movies\Batman Begins (2005) 1080p.mkv                                         | Batman Begins      | 5.0            | 1080p      |       |         |                       | Duplicate - partial  | A film with 1080p already exists. Could not extract and check codec/media from filename. link |
| C:\Movies\A made up film (2001) 1080p H264 Blu-ray group_name.mkv                | A made up film     | 10.0           | 1080p      | H264  | Blu-ray | group_name            | Duplicate                                                                  | Exact filename already exists: link  |
| C:\Movies\25th Hour 2002 1080p BluRay DTS x264-GrapeHD.mkv                       | 25th Hour          | 18.9           | 1080p      | H264  | Blu-ray | grapehd            | Duplicate                                               | A film with 1080p/H264/Blu-ray already exists: link     |


| C:\Movies\A.bad.film.2022.720p.WEB-DL.DD5.1.H.264-YIFY.mkv                       | A bad film         | 1.0            | 720p       | H264  | Web     | yify                  | Banned                                                                          | Release group 'yify' is banned from ANT - do not upload|




## How does it work?

The process searches through the given directory (or multiple directories), and finds all common video file formats (currently: mp4, avi, mkv, mpeg and m2ts). Using an existing package called [guessit](https://github.com/guessit-io/guessit) and some additional processing, film titles and their  properties are parsed. For each film, a get request is sent to ANT's API, to check whether it can be found already. For certain titles, if an initial match is not found, the title is tweaked and re-searched. For example, films containing "and" could be spelt with "and" or "&", so both titles are checked.

The script outputs a csv file containing a list of films it's found and whether they've been found on ANT or not, and whether they are duplicates.

If an existing film_list.csv is found in the output location specified, any films in this that have already been found on ANT and are marked as duplicates (from version 1.7.0) will be skipped by the process. This means you can re-run the script without having to search through your whole film library again. It will not skip films that were not found on ANT or those that were not marked as duplicates (in case they've since been uploaded).

This is a work in progress - please feel free to give helpful feedback and report bugs.

## Known issues
* Non-english films may not be found on ANT if their titles do not match
* Films with ellipsis may not be found. Currently guessit automatically removes these e.g. Tick Tick... BOOM! -> Tick Tick Boom!
* Films with alternate titles (Film X AKA Film Y) will not be found on ANT
* Some users are unable to use the script with a GUI (graphical user interface)- an alternative option will be added in the future

## Prerequisites
* You must have Python v 3.8 or later installed: https://www.python.org/downloads/windows/
* You must be a member of ANT
    * Please do not message me for an invite, or open issues requesting one, these will be ignored. ANT Staff is aware of and monitors this repo
* If you are on Linux, note that some Python installations don't come with a package called Tkinter which is required. 
    * If you are prompted to install it, choose the command based on your Linux system, or see here for more info: https://stackoverflow.com/questions/4783810/install-tkinter-for-python
        * **Debian/Ubuntu:** `sudo apt install python3-tk -y`
        * **Fedora:** `sudo dnf install -y python3-tkinter`
        * **Arch:** `sudo pacman -Syu tk --noconfirm` 
        * **REHL/CentOS6/CentOS7:** `sudo yum install -y python3-tkinter`
        * **OpenSUSE:** `sudo zypper in -y python-tk`

## How to setup and run ant_upload_checker
1. **Optional step: setup a virtual environment** (recomended but not required)
    * A virtual environment lets you install a package and its dependencies in a contained area, keeping it seperate from other Python projects on your system. It's good practise to use a virtual environment, but if you're not fussed about running other Python projects, or if you want to install it globally instead, feel free to skip this step (see https://docs.python.org/3/tutorial/venv.html for more info)
    * Navigate to where you want to store the package
    * From the command line (e.g. Command Prompt) type `python -m venv .venv`. This should create a folder called .venv containing the virtual environment.
    * Then activate the virtual environment
        * Windows: If in a Command Prompt, type `.venv/Scripts/activate`. If using PowerShell, type `.venv/Scripts/Activate.ps1`
        * Linux: `source .venv/bin/activate`
2. **Install the package**
    * From the command line (e.g. Command Prompt) type `pip install ant-upload-checker`. This should install the package from [PyPI](https://pypi.org/project/ant-upload-checker/)
3. **Run the package**
    * Once installed, type `ant-upload-checker` to run the package
    * You should be asked for your ANT API key - you can paste this in after copying it from ANT
    * A dialog box should then open asking for your input folders (where your films are stored)
    * Finally, another dialog box should ask you to specify your output folder (where the film list CSV should be written)
    * When you run it for a second time, you can skip this stage by selecting "No" when asked whether you want to overwrite your existing settings
4. **Check the output file**
    * Open the output csv file to see which films already exist on the tracker
    * Please remember this is a work in progress - feel free to report any issues you come across!

### How to update to the latest version
Assuming you've already installed ant_upload_checker, type `pip install --upgrade ant-upload-checker`. If there's a new version available, it should update the version you have installed. 

Remember that if you originally installed the package into a virtual environment, you will need to first activate the virtual environment again (navigate to the folder, type `.venv/Scripts/Activate.ps1` for Windows or `source .venv/bin/activate` for Linux)

### How to work on the code
If you want to do any development work, don't install from PyPi. Instead:
1. Git clone the repository
2. Setup a virtual environment in the root directory (see step 1 of 'How to setup and run ant_upload_checker'). 
3. In the command line type `pip install -e .[test]`. This should install the package and the optional test dependencies.


### Planned improvements
- [ ] Continue to add more film properties to dupe check
- [ ] Continue code refactor, finish adding type hints
- [ ] Add a CLI for those unable to use GUI
- [ ] Increase max file path length
- [ ] Add automatic torrent creator using torf

See the [changelog](changelog.md) for recent changes.

