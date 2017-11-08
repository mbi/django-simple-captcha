#!/bin/bash
export CAPTCHA_FLITE_PATH=`which flite`
export CAPTCHA_SOX_PATH=`which sox`
coverage run --rcfile .coveragerc  manage.py test --failfast captcha
coverage xml
coverage html
