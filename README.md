# fuelmeter-tools


## dev setup

This project uses a `Pipfile` to manage library dependancies using the pipenv
tool. See pytohn tutorials for using [pipenv for managing depenacies](https://packaging.python.org/tutorials/managing-dependencies/). Pipenv is good but there are some some valid [gripes](https://hynek.me/articles/python-app-deps-2018/).

To install pipenv do this:

* `pip install --user pipenv`

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

