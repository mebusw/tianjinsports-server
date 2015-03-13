#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import time
from django.utils.datetime_safe import datetime

from django.db import models
from django.contrib.auth.models import User

from peggy.lib.django_qiniu.fields import QiNiuImageField, QiNiuFileField


def qiniu_key_maker_file(instance, filename):
    """
    Args:
    ~~~~~
    - instance, your model instance being saved
    - filename, original filename

    This function should return a string object which is the key of qiniu.
    """
    return os.path.basename(filename)


def qiniu_key_maker_image(instance, filename):
    # print filename
    return os.path.basename(filename)


class Photo(models.Model):
    # qiniu_file = QiNiuFileField(upload_to=qiniu_key_maker_file, null=True)
    qiniu_image = QiNiuImageField(upload_to=qiniu_key_maker_image, null=True)

    class Meta:
        app_label = 'peggy'


class Customer(models.Model):
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = ((GENDER_MALE, '男'), (GENDER_FEMALE, '女'),)

    user = models.OneToOneField(User)
    birthday = models.DateTimeField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True, null=True)
    weixin = models.CharField(max_length=20, blank=True, null=True)
    alipay = models.CharField(max_length=40, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    avatar_url = models.URLField(max_length=200, blank=True, null=True)
    referrer_mobile = models.CharField(max_length=20, blank=True, null=True, default='')
    point = models.BigIntegerField(default=0)
    create_date = models.DateTimeField(max_length=100, blank=True, null=True, auto_now_add=True)
    update_date = models.DateTimeField(max_length=100, blank=True, null=True)
    last_checkin_time = models.DateTimeField(max_length=100, blank=True, null=True, auto_now_add=True)

    class Meta:
        app_label = 'peggy'

    @property
    def age(self):
        today_aware = datetime.today()
        return today_aware - self.birthday

    def __unicode__(self):
        return u'%s @ %s' % (self.user.username, self.point)


class SurveyResult(models.Model):
    user = models.ForeignKey(User)
    answers = models.CharField(max_length=5000)  # A json string contains answers of all questions.
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u"%s %s" % (self.user, self.create_date)


class Order(models.Model):
    CREATED = 'CREATED'
    PAID = 'PAID'
    PRODUCED = 'PRODUCED'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    CONSUMED = 'CONSUMED'
    CANCELLED = 'CANCELLED'
    STATE_CHOICES = ((CREATED, '已创建'), (PAID, '已支付'), (PRODUCED, '已调配'), (SENT, '已发货'), (DELIVERED, '已签收'),
                     (CONSUMED, '已使用'), (CANCELLED, '已取消'))

    user = models.ForeignKey(User)
    survey_result = models.ForeignKey(SurveyResult, null=True)
    out_trade_no = models.CharField(max_length=255, null=True, blank=True)
    express_no = models.CharField(max_length=255, null=True, blank=True)
    express_vendor = models.CharField(max_length=255, null=True, blank=True)
    total_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    deliver_date = models.DateTimeField(null=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=CREATED)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u'￥%s (%s) for %s - %s - %s' % (
            self.discount_price, self.total_price, self.user.username, self.state, self.out_trade_no)


class RefundClaim(models.Model):
    CREATED = 'CREATED'
    REFUNDED = 'REFUNDED'
    STATE_CHOICES = ((CREATED, '已创建'), (REFUNDED, '已返现'))

    user = models.ForeignKey(User)
    point = models.BigIntegerField(default=0)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, blank=True, null=True, default=CREATED)
    create_time = models.DateTimeField(auto_now_add=True)
    refund_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u'%spts of %s - %s' % (self.point, self.user, self.state)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    price = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u'%s / ￥%s' % (self.name, self.price)


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    amount = models.IntegerField(max_length=10, default=0)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u'%s %s x%s @ %s' % (self.product.name, self.product.price, self.amount, self.order.id)


class Article(models.Model):
    ARTICLE = 'ARTICLE'
    BULLETIN = 'BULLETIN'
    TYPE_CHOICES = ((ARTICLE, '文章'), (BULLETIN, '公告'))

    create_time = models.DateTimeField(auto_created=True, null=True)
    title = models.CharField(max_length=255)
    cover_img_url = models.URLField()
    text = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=ARTICLE)

    class Meta:
        app_label = 'peggy'

    def __unicode__(self):
        return u'%s' % (self.title)


class Comment(models.Model):
    user = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=140)

    class Meta:
        app_label = 'peggy'

#
# class Poll(models.Model):
# SINGLE_CHOICE = 'SINGLE_CHOICE'
# SINGLE_CHOICE_W_FREE_TEXT = 'SINGLE_CHOICE_W_FREE_TEXT'
#     MULTI_CHOICE = 'MULTI_CHOICE'
#     MULTI_CHOICE_W_FREE_TEXT = 'MULTI_CHOICE_W_FREE_TEXT'
#     FREE_TEXT = 'FREE_TEXT'
#
#     FORM_CTRL_TYPE_CHOICES = ((SINGLE_CHOICE, SINGLE_CHOICE), (SINGLE_CHOICE_W_FREE_TEXT, SINGLE_CHOICE_W_FREE_TEXT),
#                               (MULTI_CHOICE, MULTI_CHOICE), (MULTI_CHOICE_W_FREE_TEXT, MULTI_CHOICE_W_FREE_TEXT),
#                               (FREE_TEXT, FREE_TEXT))
#
#     question = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#     form_ctrl_type = models.CharField(max_length=30, choices=FORM_CTRL_TYPE_CHOICES, default=SINGLE_CHOICE)
#
#     def was_published_recently(self):
#         return self.pub_date >= time.now() - datetime.timedelta(days=1)
#
#     was_published_recently.admin_order_field = 'pub_date'
#     was_published_recently.boolean = True
#     was_published_recently.short_description = 'Published recently?'
#
#     class Meta:
#         app_label = 'peggy'
#
#     def __unicode__(self):
#         return self.question
#
#
# class Choice(models.Model):
#     poll = models.ForeignKey(Poll)
#     statement = models.CharField(max_length=200)
#
#     class Meta:
#         app_label = 'peggy'
#
#     def __unicode__(self):
#         return "%s for %s" % (self.statement, self.poll.question)
#
#
# class Opinion(models.Model):
#     user = models.ForeignKey(User)
#     choice = models.ForeignKey(Choice)
#     free_text = models.CharField(max_length=200, null=True)
#
#     class Meta:
#         app_label = 'peggy'
#
#     def __unicode__(self):
#         return "%s(%s) for %s by %s" % (self.choice.statement, self.free_text, self.choice.poll.question, self.user.username)
