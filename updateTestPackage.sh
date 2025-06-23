#!/bin/bash
. "./venv/bin/activate"
git pull
rm dist/*
python setup.py bdist_wheel sdist
twine upload --repository testpypi --verbose dist/*dev*