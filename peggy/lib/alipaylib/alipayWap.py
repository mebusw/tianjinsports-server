#!/usr/bin/env python
# encoding: utf-8
'''
Created on 2015-1-11
@author: mebusw@163.com
'''
from xml.etree import ElementTree as ET
import hashlib
import urllib2, urllib
import alipayConfig
from collections import OrderedDict

verifyURL = {
    "https": "https://mapi.alipay.com/gateway.do?service=notify_verify",
}
gateway_classic = "https://mapi.alipay.com/gateway.do"
gateway_wap = "http://wappaygw.alipay.com/service/rest.htm"


class Alipay(object):
    def __init__(self):
        self.conf = {
            'partner': alipayConfig.partner,
            'seller_email': alipayConfig.seller_mail,
            'notify_url': alipayConfig.notify_url,
            'return_url': alipayConfig.return_url,
            'show_url': alipayConfig.show_url,
            '_input_charset': "UTF-8",
            'sign_type': "MD5",
            'key': alipayConfig.key,
            # 其他参数，如果有默认值定义在下面：
            'paymethod': "",
            'mainname': "",
        }

    def is_correct_sign(self, params, should_sort_keys=True):
        sign = params.get('sign', None)
        local_sign = self.build_md5_sign(params, should_sort_keys)

        if sign is None or local_sign != sign:
            print 'sign error, notify sign=%s     local sign=%s' % (sign, local_sign)
            return False
        return True

    def build_md5_sign(self, params, should_sort_keys=True):
        populated = self.populate_url_str(params, should_sort_keys)
        sign = hashlib.md5((populated + self.conf['key']).encode('utf-8')).hexdigest()
        # print "md5 sign is %s" % sign
        return sign

    def populate_url_str(self, params, should_sort_keys=True):
        ks = params.keys()

        if should_sort_keys:
            ks.sort()

        rlt = ''
        for k in ks:
            if params[k] is None or len(params[k]) == 0 or k == "sign" or k == "sign_type" or k == "key":
                continue
            rlt += "&%s=%s" % (k, params[k])
        # print "URL:" + rlt[1:]
        return rlt[1:] #.encode('utf8')


class AlipayWap(Alipay):
    def __init__(self, *args, **kw):
        Alipay.__init__(self, *args, **kw)

    def make(self, out_trade_no, subject, total_fee):
        token = self.step1_fetch_token(out_trade_no, subject, total_fee)
        # print 'token_mw=', token
        return self.step2_execute_payment(token, out_trade_no)

    def step1_fetch_token(self, out_trade_no, subject, total_fee):
        url, url_values = self._compose_token_request(out_trade_no, subject, total_fee)
        # print url, url_values
        resp = urllib2.urlopen(url, url_values)
        #print '=========================='
        decoded = urllib.unquote_plus(resp.read())
        # print decoded
        return self._parse_token(decoded)

    def _compose_token_request(self, out_trade_no, subject, total_fee):
        params = {
            '_input_charset': self.conf['_input_charset'],
            'format': 'xml',
            'partner': self.conf['partner'],
            'req_data': ('<direct_trade_create_req><notify_url>%s</notify_url><call_back_url>%s</call_back_url><seller_account_name>%s</seller_account_name><out_trade_no>%s</out_trade_no><subject>%s</subject><total_fee>%s</total_fee></direct_trade_create_req>'
                        % (self.conf['notify_url'], self.conf['return_url'], self.conf['seller_email'], out_trade_no, subject, total_fee)),
            'req_id': out_trade_no,
            'sec_id': self.conf['sign_type'],
            'service': 'alipay.wap.trade.create.direct',
            'v': '2.0'
        }
        sign = self.build_md5_sign(params)
        params['sign'] = sign
        params['req_data'] = params['req_data'].encode('utf8')
        url_values = urllib.urlencode(params)
        url = gateway_wap
        return url, url_values

    def _parse_token(self, s):
        return s[s.index('<request_token>') + len('<request_token>'): s.index('</request_token>')]

    def step2_execute_payment(self, token, out_trade_no):
        params = {
            'format': 'xml',
            'partner': self.conf['partner'],
            'req_data': '<auth_and_execute_req><request_token>%s</request_token></auth_and_execute_req>' % token,
            'req_id': out_trade_no,
            'sec_id': self.conf['sign_type'],
            'service': 'alipay.wap.auth.authAndExecute',
            'v': '2.0'
        }
        sign = self.build_md5_sign(params)
        params['sign'] = sign
        return self._create_pay_form(params, "GET")

    def _create_pay_form(self, params, method="GET", title="确认，支付宝付款"):
        """
            生成提交到支付宝的表单，用户通过此表单将订单信息提交到支付宝。
        """
        ele = ""
        for nm in params:
            # print "key in params : %s=%s" % (nm, params[nm])
            if params[nm] is None or len(params[nm]) == 0 or nm == '_input_charset':
                continue
            ele += " <input type='hidden' name='%s' value='%s' />" % (nm, params[nm])

        html = '''<form name='alipaysubmit' action='%s?_input_charset=%s' method='%s'>
                %s
                <input type="submit" value="%s" />
            </form>
            ''' % (gateway_wap, self.conf['_input_charset'], method, ele, title)
        html += "<script>document.forms['alipaysubmit'].submit();</script>"
        # print html
        return html

    def notify_call(self, params, verify=True, transport="https", check_sign=True):
        """
          校验支付宝返回的参数，交易成功的通知回调.
          校验分为两个步骤：检查签名是否正确、访问支付宝确认当前数据是由支付宝返回。

          params为支付宝传回的数据。
        """
        fixed_params = OrderedDict()
        fixed_params['service'] = params['service']
        fixed_params['v'] = params['v']
        fixed_params['sec_id'] = params['sec_id']
        fixed_params['notify_data'] = params['notify_data']
        fixed_params['sign'] = params['sign']
        # print fixed_params

        if check_sign and not self.is_correct_sign(fixed_params, should_sort_keys=False):
            print 'sign wrong'
            return "fail"

        t = ET.fromstring(params['notify_data'].encode('utf8'))
        trade_status = t.find('trade_status').text
        if trade_status != 'TRADE_FINISHED' and trade_status != 'TRADE_SUCCESS':
            print 'status wrong', trade_status
            return "fail"

        if not verify:
            return "success"
        else:
            print "Verify the request is call by alipay.com...."
            url = verifyURL[transport] + "&partner=%s&notify_id=%s" % (self.conf['partner'], t.find('notify_id').text)
            response = urllib2.urlopen(url)
            html = response.read()

            print "aliypay.com return: %s" % html
            if html == 'true':
                return "success"

            return "fail"


if __name__ == '__main__':
    alipayWap = AlipayWap()
    alipayWap.make()
    # alipayMW.step1_fetch_token()
    # alipayMW.step2_execute_payment(token='123')



