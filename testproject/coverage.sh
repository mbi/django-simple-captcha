#!/bin/bash
export CAPTCHA_FLITE_PATH=`which flite`
coverage run --rcfile .coveragerc  manage.py test --failfast captcha
coverage xml
coverage html
