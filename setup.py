from setuptools import setup

setup(
   name='ant_upload_checker',
   version='1.0',
   description='Check if films in input directory are already uploaded to Anthelion',
   author='pizzaolive',
   packages=['ant_upload_checker'], 
   install_requires=["pandas","requests","ratelimit","pytest"],
)