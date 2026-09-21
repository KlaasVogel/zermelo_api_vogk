#!/bin/bash
git pull
rm -f dist/*
pyproject-build --sdist --wheel
rm -f dist/*.dev*
twine upload --verbose dist/*