# Working on the code

### Setup and activate a venv
See here for more details: https://docs.python.org/3/library/venv.html

On Windows:
```
python -m venv venv
venv\Scripts\Activate.ps1   
```

### Install the requirements
```
pip install -r dev_requirements\requirements.txt
```

### Updating the packages used
* Update the packages listed within setup.py
* Install pip tools: `python -m pip install pip-tools`
* Run pip-compile to create a new requirements.txt file: `pip-compile --output-file=- > dev_requirements\requirements.txt`