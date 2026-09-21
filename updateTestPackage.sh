#!/bin/bash
git pull
rm -f dist/*
pyproject-build --sdist --wheel
twine upload --repository testpypi --verbose dist/*dev*