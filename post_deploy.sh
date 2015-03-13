#!/bin/sh
chown www-data .
chown www-data ./sqlite3_db
chmod u+w+x,g+w+x ./sqlite3_db
python manage.py migrate
python manage.py  collectstatic --noinput
/etc/init.d/apache2 restart

