#!/bin/bash
. "./venv/bin/activate"
git pull
python setup.py bdist_wheel sdist
twine upload --verbose dist/*
