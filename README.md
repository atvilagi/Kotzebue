# fuelmeter-tools

This is a collection of data management and mangling tools developed to support
the ACEP fuelmeter project.

## Contributing

The repository, content within, and contributions are licensed under MIT license.

## other tools used

* [click](https://github.com/pallets/click) - cli tool builder helper (alternative to argparse)
* jupyter - data lab
* [pandas](https://pandas.pydata.org/) - data analysis and modeling library
* [plotly](https://plot.ly/python/plotly-fundamentals/) - data visualization
* [ubidots-python](https://github.com/ubidots/ubidots-python) - 
* [python-dotenv](https://github.com/theskumar/python-dotenv) - parsing .env
  files

## dev setup

This project uses a `Pipfile` to manage library dependancies using the pipenv
tool. See pytohn tutorials for using [pipenv for managing depenacies](https://packaging.python.org/tutorials/managing-dependencies/). Pipenv is good but there are some some valid [gripes](https://hynek.me/articles/python-app-deps-2018/).


To install pipenv do this:
* `pip3 install --user pipenv`
* The above installs pipenv to `$HOME/.local/bin` which will need to be in `$PATH`.  If that is missing add following line to `.bashrc`
  `export PATH=$PATH:$HOME/.local/bin`

To install project dependancies:
* `pipenv update`

Running a script here with neccessary depenacies in the python environment:
```
pipenv run python PROJECT-SCRIPT-HERE
``

To launch a shell where all these depenacies are available run: 
```
pipenv shell
```

Developer here and want to use a new library, for example `plotly`, you just:
```
pipenv install plotly
# verify things work well and you are happy
git add Pipfile
# hack hack, commit & push
```

