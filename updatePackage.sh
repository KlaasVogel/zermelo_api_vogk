#!/bin/bash
. "./venv/bin/activate"
git pull
rm dist/*.dev*
python setup.py bdist_wheel sdist
twine upload --verbose dist/*
