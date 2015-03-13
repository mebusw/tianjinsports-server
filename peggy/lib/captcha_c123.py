#!/usr/bin/env python
# encoding: utf-8

from peggy.lib import xmltodict
import urllib2
from random import randint

C123_URL = 'http://smsapi.c123.cn/OpenPlatform/OpenApi?'

#http://smsapi.c123.cn/OpenPlatform/OpenApi?action=sendOnce&ac=1001@501116660001&authkey=0233299A88840252FC475B645A588768&cgid=52&csid=501116660001&c=打死也不能说！&m=18622398401
AC = '1001@501116660001'
AUTH_KEY = '0233299A88840252FC475B645A588768'
CGID = '52'
CSID = '501116660001'
SMS_TXT = '打死也不能说！'


def send_sms(captcha, to_mobile):
    url = C123_URL + 'action=sendOnce&ac=%s&authkey=%s&cgid=%s&csid=%ss&c=%s%s&m=%s' \
                     % (AC, AUTH_KEY, CGID, CSID, SMS_TXT, captcha, str(to_mobile))
    print url
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    xml_str = req.read().decode('utf-8')
    converted_dict = xmltodict.parse(xml_str)
    return converted_dict


def generate_captcha():
    return str(randint(1000, 9999))
