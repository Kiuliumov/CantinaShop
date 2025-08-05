#!/bin/bash

source /antenv/bin/activate

export DJANGO_SETTINGS_MODULE=CantinaShop.settings

# shellcheck disable=SC2164
cd theme/static_src
npm install
cd ../../

python manage.py tailwind build

python manage.py migrate --noinput
python manage.py collectstatic --noinput

cat <<EOF > Procfile
web: python runserver.py
worker: python runceleryworker.py
EOF

pip install honcho
exec honcho start
