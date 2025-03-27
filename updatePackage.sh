#!/bin/bash
. "./venv/bin/activate"
git pull
del /dist/*.dev*
python setup.py bdist_wheel sdist
twine upload --verbose dist/*
