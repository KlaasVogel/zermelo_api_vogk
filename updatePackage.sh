#!/bin/bash
. "./venv/bin/activate"
git pull
# rm dist/*.dev*
rm dist/*
python setup.py bdist_wheel sdist
twine upload --verbose dist/*