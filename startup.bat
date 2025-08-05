@echo off

REM Activate virtual environment
call C:\Users\admin\PycharmProjects\CantinaShopProject\.venv\Scripts\activate.bat

REM Set Django settings module environment variable
set DJANGO_SETTINGS_MODULE=CantinaShop.settings

python manage.py collectstatic --noinput
python manage.py migrate --noinput

start /B python runserver.py

python runceleryworker.py
