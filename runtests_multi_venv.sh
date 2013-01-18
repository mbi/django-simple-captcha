#!/bin/bash

# You'll have to create three virtualenvs and pip install PIL and django 1.3, 1.4 and 1.5 in either one.
# Once django 1.5 is released I'll probably try to automate this

. venv_13/bin/activate
cd testproject
python manage.py --version
python manage.py test captcha
cd ..
deactivate

. venv_14/bin/activate
cd testproject
python manage.py --version
python manage.py test captcha
cd ..
deactivate

. venv_15/bin/activate
cd testproject
python manage.py --version
python manage.py test captcha
cd ..
deactivate

