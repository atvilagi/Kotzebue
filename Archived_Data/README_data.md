# Python Scripts

Here are the python scripts used in packaging the PuMA fuel metere data. They are designed to be run in a pipenv environment. Instructions can be found in the repository main folder README file.

## Pipfile

The Pipfile describes the dependencies used in the pipenv environment runtime. Edit this if script dependencies have changed. It produces a Pipfile.lock when initiated.

## prod_nc2csv.py

This script takes the puma_unified_data.nc file and converts it into csv files for simpler cross platform use.

## puma2uni_nc.py

This script takes the text files collected from the fuel meters and stored in the ftp-data directory, extracts the data and places it into an organized netCDF file (using the puma-inventory.yml file) with the stove information, fuel consumption, and temperature information.

## pumapy.py

This file contains all the functions used in the scripts for data packaging.

## uni_nc2prod_nc.py

This script transcribes the puma_unified_data.nc file into a reduced puma_product_data.nc file.
