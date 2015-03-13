TianjinSports
=============

![](https://magnum.travis-ci.com/go2imagination2/peggy.svg?token=RmBVkFRFqqdF5pssRifi)

## Dependencies
* Django 1.7.5
* mock
* fabric
* gunicorn

## SQLite
``` 
python manage.py dbshell
.tables
drop table peggy_xxx 
```

## 阿里云 
mebusw@163.com

i-25p15bj1r
ssh root@123.57.88.24

* 远程免登录
**L** .ssh/id_rsa.pub
**R** .ssh/authorized_keys

# TODO

报名功能
DB design
django
pg-geo plugin
phonegap cloud - adhoc .p12


## Deploy
* Below models should be imported all at once when deploy to production.
They also have been dumped as test fixtures.

```
python manage.py dumpdata --indent=2 auth.group auth.user peggy.customer peggy.product peggy.article peggy.order peggy.orderitem peggy.surveyresult peggy.refundclaim > peggy/fixtures/peggy.json
python manage.py loaddata peggy/fixtures/peggy.json
```

## Nginx+Mysql+Apache2(phpmyadmin)

```
chown www-data .
chown www-data ./sqlite3_db
chmod u+w+x,g+w+x ./sqlite3_db
python manage.py migrate
python manage.py  collectstatic --noinput
gunicorn --workers=2 mysite.wsgi:application
````

* gnunicorn (on linux) or PyISAPIe (on Windows IIS)
* enable necessary cache
* CDN/ETag (http 304)
* disable DEBUG
* uglify/cssmin/figureprint
* ga/cnzz



## Apache2
    /etc/init.d/apache2 restart
    
``` vi /etc/apache2/sites-available/default
        Alias /static/ /srv/peggy/static/
        WSGIScriptAlias / /srv/peggy/mysite/wsgi.py
        <Directory /srv/peggy/mysite>
                <Files wsgi.py>
                Order deny,allow
                Allow from all
                </Files>
        </Directory>
```

``` vi /etc/apache2/httpd.conf
        WSGIPythonPath /srv/peggy
```

``` vi /etc/apache2/ports.conf
        Listen 8001
```

## Nginx

    nginx
    nginx -s stop
    
``` vi /etc/nginx/nginx.conf
    server {
        server_name     peggysbeauty.com;
            location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host  $http_host;
                proxy_set_header X-Forwarded-For  $remote_addr;
            }
        
            location  /static/ {
                alias /srv/peggy/static/;
            }
        
            location /phpmyadmin {
                proxy_pass http://127.0.0.1:8001/phpmyadmin;
            }
        }
    }
```
