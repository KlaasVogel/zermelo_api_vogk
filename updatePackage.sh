#!/bin/bash
. "./venv/bin/activate"
git pull
rm dist/*
python setup.py bdist_wheel sdist
rm dist/*.dev*
twine upload --verbose dist/*