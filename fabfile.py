from fabric.api import local, run


def host_type():
    """fab host_type -H 123.57.88.24 -u root
    """
    run('uname -s')


def ver():
    """fab ver
    """
    local('fab --version')
    local('python --version')
    local('python manage.py version')


def post_deploy():
    """fab post_deploy
    """
    local('chown www-data .')
    local('chown www-data ./sqlite3_db')
    local('chmod u+w+x,g+w+x ./sqlite3_db')
    local('python manage.py migrate')
    local('python manage.py  collectstatic --noinput')
    local('python manage.py loaddata peggy/fixtures/peggy.json')
    #local('/etc/init.d/apache2 restart')
    local('pkill gunicorn')
    local('gunicorn --workers=2 mysite.wsgi:application &')
