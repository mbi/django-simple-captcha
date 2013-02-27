#!/bin/bash

# You'll have to create three virtualenvs and pip install PIL and django 1.3, 1.4 and 1.5 in either one.
# venv_15_p3 tests against Django 1.5 and Python 3.3

export CAPTCHA_FLITE_PATH=`which flite`

. venv_13/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

. venv_14/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

. venv_15/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate


. venv_15_p3/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate
