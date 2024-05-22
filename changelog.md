Version 1.4.5
* Add additional film info to output CSV (codec and source, release group)
* If output directory doesn't exist, it is now automatically created
* Minor code refactors

Version 1.4.4
* Films with potential alternate titles (e.g. Film 1 AKA Film 2) are now split apart and re-searched if not initially found (closes Issue #4).
* Tidier logging formatting.

Version 1.4.3
* Process now checks if a film's specific resolution is already uploaded to ANT as well. If the resolution is missing then it can likely be uploaded even if the film exists on ANT. If the resolution can't be extracted from the file name, then it will just check if it exists on ANT.
* If a film_list.csv is found from previous versions, this won't be compatible with this new update, so if a file is found, this is backed up in case users want this to be kept.
* Fixed error handling logging messages and added messages for specific status codes user might encounter.

Version 1.4.2 
* Attempt fix for an issue where films with titles containing numbers (potential times or dates) were not found. These are now re-searched if not found.
    * E.g. Fahrenheit 911 -> Fahrenheit 9/11. Test film 1008 -> Test film 10:08
* Add error handling to API call
* Add tests
* Re-factor search for film func

Version 1.4.1
* Add ability to specify multiple input folders in parameters, so that several directories can be scanned for films at once

Version 1.4
* If an existing film_list.csv is found in the output location specified, any films in this csv that have already been found on ANT will be skipped by the process. This means you can re-run the script without having to search through your whole film library again. It will not skip films that were previously not found on ANT, and any new films in your library.
* Code has been reformatted into classes, new functions relating to above added, more tests added

Version 1.3.1
* Output now provides the size of the film in GB
* Reformatted some code, added test

Version 1.3
* Films containing "&" or "and" are re-searched if not initially found, with "&" or "and" substituted. Should improve film title matching.

Version 1.2
* Add additional video container formats
* Improved film title parsing: now uses 'guessit' package alongside own regex functions
* Added tests, more film test cases
* Improved logging info including note in terminal if a film is not found on ANT

Version 1.1
* Remove Extras folder being parsed as NA and searched
* Add m2ts extension to the file search
* Remove old optional argument to only search for 5 films

Version 1.0
* Published git repo
