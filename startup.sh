#!/bin/bash

source /antenv/bin/activate

export DJANGO_SETTINGS_MODULE=CantinaShop.settings

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python runserver.py &
python runceleryworker.py
