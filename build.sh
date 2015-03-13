RUNNER="python manage.py"
$RUNNER syncdb
$RUNNER test $1
$RUNNER runserver
