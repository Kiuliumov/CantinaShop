#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput

export DJANGO_SETTINGS_MODULE=CantinaShop.settings

python runserver.py &

python runceleryworker.py
