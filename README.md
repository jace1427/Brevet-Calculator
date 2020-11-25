# Project 6: Brevet time calculator service

Simple listing service from project 5 stored in MongoDB database.

Author: Justin Spidell

Contact: jspidell@uoregon.edu

## What is in this repository

flask_brevets: The backend logic for the app
acp_times.py: Logic for calculating the open and close times
config.py: Configurations for the app
calc.html: The html for the main page
display.html: The html for the display page
index.php: The php for api page
docker-compose.yml: Build the whole project

## How to Use

Run 'bash run.sh' in a terminal from /DockerRestApi. Go to http://localhost:5001/ then to http://localhost:5000/ from any browser.

## Tests / Errors

The page will automaticly clear your entry if you do not enter a number into miles or km. It will display an error if you submit an empty form. Likewise it will display an error if you try to display entries before you submit. The program is designed to ignore any field in the form that does not have any entries. The Page will 404 if you try to go to any page that does not exsist.

## Brevet Calculations

Using the table found at https://rusa.org/pages/acp-brevet-control-times-calculator:

Opening times are calculated by dividing the control location by the coorisponding maximum speed. For every following control location, divide the distance from the previous control location by the maximum speed that coorisponds to the current running total.

Closing times are calculated by dividing the control location by the coorisponding minmum speed. For every following control location, divide the distance from the previous control location by the minmum speed that coorisponds to the current running total.