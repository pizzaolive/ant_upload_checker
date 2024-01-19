Version 1.3.1
* Output now provides the size of the film in GB
* Reformatted some code, added test
* Paths now sorted after initial path search

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