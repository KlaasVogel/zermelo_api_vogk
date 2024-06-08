call venv\Scripts\activate
call python setup.py sdist
call pip install .
call python run.py