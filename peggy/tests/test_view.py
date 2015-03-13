#!/usr/bin/python
# -*- coding: utf-8 -*-

import glob

from django.test import TestCase

from peggy.views import *
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.conf import settings
import json

class PeggyUserTest(TestCase):
    fixtures = ['peggy.json']

    @classmethod
    def setUpClass(cls):
        pass


    # @classmethod
    # def tearDownClass(cls):
    # for f in glob.glob(settings.MEDIA_ROOT + "o2o.png"):
    #         os.remove(f)

    def setUp(self):
        pass

    def testA(self):
        # print Customer.objects.all()[1].referrer.user.username
        pass

    def test_do_login_failure(self):
        response = self.client.post(reverse('peggy.views.do_login'),
                                    {'username': 'jacky', 'password': 'xxx'}, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'peggy/login.html')

    def test_do_login_success(self):
        response = self.client.post(reverse('peggy.views.do_login'),
                                    {'username': 'sj', 'password': 'sj'}, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'peggy/login.html')
        self.assertEqual(Customer.objects.get(pk=3).point, 0)

        # def test_do_registration__success(self):
        #     response = self.client.post(reverse('peggy.views.do_registration'),
        #                                 {'mobile_number': '18611112222', 'captcha': '1234', 'referrer_number': '13912345678'}, follow=True)
        #
        #     self.assertEqual(200, response.status_code)
        #     customer = Customer.objects.get(mobile_number='18611112222')
        #     self.assertEqual('13912345678', customer.referrer_number)
        #
        # def test_do_registration__mobile_already_exist(self):
        #     pass
        #
        # def test_do_registration__wrong_captcha(self):
        #     pass
        #
        # def test_do_registration__referrer_mobile_not_exist(self):
        #     pass


class PeggyFuncTest(TestCase):
    fixtures = ['peggy.json']

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.client.login(username='jacky', password='gougou')

    def test_index(self):
        response = self.client.get(reverse('peggy.views.index'))

        self.assertEqual(200, response.status_code)


class CheckinTest(TestCase):
    fixtures = ['peggy.json']

    def setUp(self):
        self.client.login(username='jacky', password='gougou')

    def test_yesterday_checked_in(self):
        right_now = datetime.now()
        yesterday = right_now - timedelta(days=1)
        c = Customer.objects.get(user__username='jacky')
        c.last_checkin_time = yesterday
        c.point = 0
        c.save()

        response = self.client.get(reverse('peggy.views.do_checkin'))

        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(0, data['error_code'])
        self.assertGreater(timedelta(seconds=3), right_now - str2dt(data['last_checkin_time']))
        self.assertEqual(0 + 2, Customer.objects.get(user__username='jacky').point)

    def test_today_already_checked_in(self):
        right_now = datetime.now()
        c = Customer.objects.get(user__username='jacky')
        c.last_checkin_time = right_now
        c.point = 0
        c.save()

        response = self.client.get(reverse('peggy.views.do_checkin'))

        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(5, data['error_code'])
        self.assertGreater(timedelta(seconds=3), right_now - str2dt(data['last_checkin_time']))
        self.assertEqual(0, Customer.objects.get(user__username='jacky').point)

        # def test_do_survey__success(self):
        # response = self.client.post(reverse('peggy.views.do_survey'),
        #                                 {'username': 'xiaobai', 'gender': 'F', 'city': 'beijing', 'mobile_number': '18612345678', 'birthday': '2013-12-02'},
        #                                 follow=True)
        #
        #     self.assertEqual(200, response.status_code)
        #     customer = Customer.objects.get(mobile_number='18612345678')
        #     self.assertEqual('xiaobai', customer.user.username)
        #     self.assertEqual('beijing', customer.city)
        #     self.assertEqual('F', customer.gender)
        #     self.assertEqual((2013, 12), (customer.birthday.year, customer.birthday.month))
        #
        # def test_do_payment__success(self):
        #     response = self.client.post(reverse('peggy.views.do_survey'),
        #                                 {'username': 'xiaobai', 'gender': 'F', 'city': 'beijing', 'mobile_number': '18612345678', 'birthday': '2013-12-02'},
        #                                 follow=True)
        #
        #     self.assertEqual(200, response.status_code)
