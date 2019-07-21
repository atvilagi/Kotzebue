# ACEP Fuel Meter Tools

This is a collection of the data management and analysis tools developed to support
the ACEP fuelmeter project.

## Licensing

The repository, content within, and contributions are licensed under MIT license.

## Data Packaging Output Files

Some scripts in the Python_Scripts folder packageAll data is collected and presented as a time series at a consistent time interval. Fuel consumption data includes the cumulative fuel pump clicks, clicks per interval, gallons consumed per interval (based off the clicks and theoretical pump flow rate), and gallons consumed per hour. The temperature data includes the indoor temperature, outdoor temperature (collected from the )

## other tools used

* [click](https://github.com/pallets/click) - cli tool builder helper (alternative to argparse)
* [jupyter notebooks] - data lab
* [pandas](https://pandas.pydata.org/) - data analysis and modeling library
* [plotly](https://plot.ly/python/plotly-fundamentals/) - data visualization
* [ubidots-python](https://github.com/ubidots/ubidots-python) - ubidots
* [python-dotenv](https://github.com/theskumar/python-dotenv) - parsing .env files

## dev setup

### pipenv

This project uses a `Pipfile` to manage library dependancies using the pipenv
tool. See pytohn tutorials for using [pipenv for managing depenacies](https://packaging.python.org/tutorials/managing-dependencies/). Pipenv is good but there are some some valid [gripes](https://hynek.me/articles/python-app-deps-2018/).


To install pipenv do this:
* `pip3 install --user pipenv`
* The above installs pipenv to `$HOME/.local/bin` which will need to be in `$PATH`.  If that is missing add following line to `.bashrc`
  `export PATH=$PATH:$HOME/.local/bin`

Update the project dependancies:
* `pipenv update`

Then install all this projects python dependancies using:
* `pipenv install`

Running a script here with neccessary dependancies in the python environment:
```
pipenv run python PROJECT-SCRIPT-HERE
```

To launch a shell where all these depenacies are available run: 
```
pipenv shell
```
```
pipenv run python -c 'from puma_data import prod_nc2csv; prod_nc2csv()'
```

Developer here and want to use a new library, for example `plotly`, you just:
```
pipenv install plotly
```
# verify things work well and you are happy

git add Pipfile

# hack hack, commit & push

## `.env` file for secrets

We use a .env file to hold secrets.  When kicking off you will want to copy

`env-sample` to `.env` like so
```
cp env-sample .env
```

Then populate with the secrets as needed.

## Enable Google Sheets API

Read the [sheeds api quickstart for python](https://developers.google.com/sheets/api/quickstart/python).

* Enable the API (see link on quickstart guide) 
* Add the the client_id and client_secret the `.env` file.
  * `SHEETS_API_CLIENT_ID=` ...
  * `SHEETS_API_SECRET=` ... 

## Contributors

Contributors to this project are:

* Bax Bond
* Dayne Broderson
* Doug Keller
