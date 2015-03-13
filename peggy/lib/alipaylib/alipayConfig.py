import os

partner = "2088711061370024"
key = "j5f5nc0lev9wch24t2cotwdvqkwexgww"
seller_mail = "17sports@sina.cn"

if 'SERVER_SOFTWARE' in os.environ:
    notify_url = "http://1.peggy.sinaapp.com/peggy/paid_notify_wap"
    return_url = "http://1.peggy.sinaapp.com/peggy/paid_wap"
    show_url = "http://1.peggy.sinaapp.com/peggy"
else:
    notify_url = "http://127.0.0.1:8000/peggy/paid_notify_wap"
    return_url = "http://127.0.0.1:8000/peggy/paid_wap"
    show_url = "http://127.0.0.1:8000/peggy"


