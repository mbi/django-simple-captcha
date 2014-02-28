#!/bin/bash

# You'll have to create three virtualenvs and pip install PIL and django 1.3, 1.4 and 1.5 in either one.
# .venv_15_p3 tests against Django 1.5 and Python 3.3

export CAPTCHA_FLITE_PATH=`which flite`


if [ ! -d .venv_14 ]
then
    virtualenv --no-site-packages --distribute --python=python2 .venv_14
    source .venv_14/bin/activate
    pip install Django==1.4 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d .venv_15 ]
then
    virtualenv --no-site-packages --distribute --python=python2 .venv_15
    source .venv_15/bin/activate
    pip install Django==1.5 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d .venv_15_p3 ]
then
    virtualenv --no-site-packages --distribute --python=python3 .venv_15_p3
    source .venv_15_p3/bin/activate
    pip install Django==1.5 Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d .venv_16 ]
then
    virtualenv --no-site-packages --distribute --python=python2 .venv_16
    source .venv_16/bin/activate
    pip install Django\>=1.6.0
    pip install Pillow==2.0.0 coverage six
    deactivate
fi
if [ ! -d .venv_16_p3 ]
then
    virtualenv --no-site-packages --distribute --python=python3 .venv_16_p3
    source .venv_16_p3/bin/activate
    pip install Django\>=1.6.0
    pip install Pillow==2.0.0 coverage six
    deactivate
fi


source .venv_14/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

source .venv_15/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate


source .venv_15_p3/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

source .venv_16/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

source .venv_16_p3/bin/activate
cd testproject
echo 'Django' `python manage.py --version`
python --version
python manage.py test captcha
cd ..
deactivate

# Make sure the PO files are well formatted
for d in `find captcha -name LC_MESSAGES -type d`; do msgfmt -c -o $d/django.mo $d/django.po; done
