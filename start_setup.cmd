call venv\Scripts\activate
call python setup.py bdist_wheel sdist
call pip install .