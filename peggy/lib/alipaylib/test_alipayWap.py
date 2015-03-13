#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from mock import Mock
from alipayWap import AlipayWap
import alipayConfig
from collections import OrderedDict

class AlipayWapTest(unittest.TestCase):
    def setUp(self):
        # alipayConfig.key = 'thisisjackyshen'
        # alipayConfig.partner = '2999999999999'
        # alipayConfig.seller_mail = 'jackyshen@scrumchina.com'
        alipayConfig.notify_url = "http://127.0.0.1:8000/sports/paid_notify_wap"
        alipayConfig.return_url = "http://127.0.0.1:8000/sports/paid_wap"

        pass

    def test_compose_token_request(self):
        url, url_values = AlipayWap()._compose_token_request("201501112309", 'JACKY-TEST', '0.01')
        expected_url = 'http://wappaygw.alipay.com/service/rest.htm'
        expected_url_values = '''v=2.0&service=alipay.wap.trade.create.direct&req_id=201501112309&format=xml&partner=2088711061370024&sec_id=MD5&sign=835b1f671c48a3ac60e9a3afd67b1dbf&_input_charset=UTF-8&req_data=%3Cdirect_trade_create_req%3E%3Cnotify_url%3Ehttp%3A%2F%2F127.0.0.1%3A8000%2Fsports%2Fpaid_notify_wap%3C%2Fnotify_url%3E%3Ccall_back_url%3Ehttp%3A%2F%2F127.0.0.1%3A8000%2Fsports%2Fpaid_wap%3C%2Fcall_back_url%3E%3Cseller_account_name%3E17sports%40sina.cn%3C%2Fseller_account_name%3E%3Cout_trade_no%3E201501112309%3C%2Fout_trade_no%3E%3Csubject%3EJACKY-TEST%3C%2Fsubject%3E%3Ctotal_fee%3E0.01%3C%2Ftotal_fee%3E%3C%2Fdirect_trade_create_req%3E'''

        self.assertEqual(expected_url, url)
        self.assertEqual(expected_url_values, url_values)

    def test_parse_token(self):
        s = '''res_data=<?xml version="1.0" encoding="utf-8"?><direct_trade_create_res><request_token>20150112b14f7f5ae62a92f7109f0c06085604c8</request_token></direct_trade_create_res>&service=alipay.wap.trade.create.direct&sec_id=MD5&partner=2088711061370024&req_id=201501121436&sign=609892298dfedea0a0860c2549392d70&v=2.0'''
        self.assertEqual('20150112b14f7f5ae62a92f7109f0c06085604c8', AlipayWap()._parse_token(s))

    def test_step2_execute_payment(self):
        expected_html = '''<form name=\'alipaysubmit\' action=\'http://wappaygw.alipay.com/service/rest.htm?_input_charset=UTF-8\' method=\'GET\'>\n                 <input type=\'hidden\' name=\'service\' value=\'alipay.wap.auth.authAndExecute\' /> <input type=\'hidden\' name=\'format\' value=\'xml\' /> <input type=\'hidden\' name=\'v\' value=\'2.0\' /> <input type=\'hidden\' name=\'req_data\' value=\'<auth_and_execute_req><request_token>20150112b14f7f5ae62a92f7109f0c06085604c8</request_token></auth_and_execute_req>\' /> <input type=\'hidden\' name=\'req_id\' value=\'201501121436\' /> <input type=\'hidden\' name=\'sec_id\' value=\'MD5\' /> <input type=\'hidden\' name=\'partner\' value=\'2088711061370024\' /> <input type=\'hidden\' name=\'sign\' value=\'e178dc16e68c15982e8e14a0df1014d0\' />\n                <input type="submit" value="\xe7\xa1\xae\xe8\xae\xa4\xef\xbc\x8c\xe6\x94\xaf\xe4\xbb\x98\xe5\xae\x9d\xe4\xbb\x98\xe6\xac\xbe" />\n            </form>\n            <script>document.forms[\'alipaysubmit\'].submit();</script>'''
        html = AlipayWap().step2_execute_payment('20150112b14f7f5ae62a92f7109f0c06085604c8', '201501121436')

        self.assertEqual(expected_html, html)

    def test_notify_call_with_sign_and_unicode(self):
        params = {u'v': u'1.0', u'sign': u'b694768df3413537c939d6ddadbbd19d', u'notify_data': u'<notify><payment_type>1</payment_type><subject>Jacky\u95f2\u901b</subject><trade_no>2015011334559446</trade_no><buyer_email>mebusw@163.com</buyer_email><gmt_create>2015-01-13 01:02:23</gmt_create><notify_type>trade_status_sync</notify_type><quantity>1</quantity><out_trade_no>20150113010217</out_trade_no><notify_time>2015-01-13 01:26:30</notify_time><seller_id>2088711061370024</seller_id><trade_status>TRADE_SUCCESS</trade_status><is_total_fee_adjust>N</is_total_fee_adjust><total_fee>0.01</total_fee><gmt_payment>2015-01-13 01:02:32</gmt_payment><seller_email>17sports@sina.cn</seller_email><price>0.01</price><buyer_id>2088002052685464</buyer_id><notify_id>671df2ab338626b927b2206bc92365f04k</notify_id><use_coupon>N</use_coupon></notify>', u'service': u'alipay.wap.trade.create.direct', u'sec_id': u'MD5'}

        result = AlipayWap().notify_call(params, verify=False)
        self.assertEqual('success', result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
