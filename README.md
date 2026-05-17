# Refinery

> _"The words of the LORD are pure words, like silver refined in a furnace on the ground, purified seven times." Psalm 12:6_

A scripture memory app based on Andrew Davis's method in [How to Memorize Scripture For Life](https://www.crossway.org/books/how-to-memorize-scripture-for-life-tpb/).


## Getting Started

After cloning this repository, you may use [Poetry](https://python-poetry.org/) with `poetry install`/`poetry run python manage.py ...` or `pip install .` with a [virtual environment](https://docs.python.org/3/library/venv.html) to install the dependencies and run the requisite `manage.py` commands for Django:

1. `manage.py migrate` - to create the database.
2. `manage.py runserver` - to start up the development server on 127.0.0.1:8000.

To use the ESV, you must have an API key from [api.esv.org](https://api.esv.org/).