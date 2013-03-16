#!/bin/bash

# You'll have to create three virtualenvs and pip install PIL and django 1.3, 1.4 and 1.5 in either one.
# venv_15_p3 tests against Django 1.5 and Python 3.3

export CAPTCHA_FLITE_PATH=`which flite`


if [ ! -d venv_13 ]
then
    virtualenv --no-site-packages --distribute --python=python2 venv_13
    . venv_13/bin/activate
    pip install Django==1.3 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d venv_14 ]
then
    virtualenv --no-site-packages --distribute --python=python2 venv_14
    . venv_14/bin/activate
    pip install Django==1.4 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d venv_15 ]
then
    virtualenv --no-site-packages --distribute --python=python2 venv_15
    . venv_15/bin/activate
    pip install Django==1.5 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d venv_15_p3 ]
then
    virtualenv --no-site-packages --distribute --python=python3 venv_15_p3
    . venv_15_p3/bin/activate
    pip install Django==1.5 Pillow==2.0.0 coverage six
    deactivate
fi




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
