#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import datetime_safe
from django.views.decorators.csrf import csrf_exempt
import json
from xml.etree import ElementTree as ET

from decorators import *
from peggy.models import *
from peggy.lib.alipaylib import AlipayWap
from peggy.lib import django_qiniu
from peggy.lib import captcha_c123
from decimal import Decimal, getcontext
from utils import *

LOGIN_URL = "/peggy/login_page"



def jsonp(request):
    return restful({'say': 'hello'})


def save_qiniu_photo(request):
    f = open("/Users/jacky/Downloads/atdd.jpg")

    photo = Photo()
    photo.qiniu_image = f
    photo.save()

    print photo.qiniu_image
    print dir(photo.qiniu_image)
    print django_qiniu.utils.get_size(f)
    # print photo.qiniu_image.get_image_view(mode=1, width=280, height=280, quality=75)
    # print photo.qiniu_image.get_image_view(mode=2, width=640, quality=75)
    return HttpResponse(photo.qiniu_image.url)


def load_qiniu_photo(request):
    # return HttpResponse(len(Photo.objects.all()))
    # print Photo.objects.get(pk=1).qiniu_image.get_image_view(mode=1, width=280, height=280, quality=75)
    return HttpResponse(Photo.objects.get(pk=5).qiniu_image.url)


def index(request):
    return render_to_response('peggy/index.html',
                              {"btn1_navbar_active": "active"}
                              , context_instance=RequestContext(request))


def do_send_captcha(request):
    """ 服务器向指定手机发送手机短信码，发送间隔不小于30s。
    :param request:
    :return:
    """

    mobile = request.GET['mobile']

    # TODO 发送间隔不小于30s
    captcha = captcha_c123.generate_captcha()
    send_time = dt2str(datetime.now())

    converted_dict = captcha_c123.send_sms(captcha, mobile)

    if '1' == converted_dict['xml']['@result']:
        request.session['sent_captcha'] = captcha
        request.session['to_mobile'] = mobile
        request.session['send_time'] = send_time
        return restful({'to_mobile': mobile, 'send_time': send_time})
    else:
        return restful({'to_mobile': mobile}, error_code=5, error_msg='fail to send captcha')


def registration_page(request, msg=""):
    return render_to_response('peggy/registration.html', {},
                              context_instance=RequestContext(request))


def do_registration(request):
    mobile = request.POST["mobile"]
    captcha = request.POST["captcha"]
    first_name = request.POST["first_name"]
    password = request.POST["password"]
    referrer_mobile = request.POST["referrer_mobile"]

    if 'sent_captcha' not in request.session or request.session['sent_captcha'] != captcha:
        return render_to_response('peggy/registration.html', {
            'msg': '验证码不正确',
        }, context_instance=RequestContext(request))

    if len(User.objects.filter(username=mobile)) > 0:
        return render_to_response('peggy/registration.html', {
            'msg': '手机号已注册',
        }, context_instance=RequestContext(request))

    user = User(username=mobile, first_name=first_name)
    user.set_password(password)
    user.save()

    customer = Customer(user=user)
    customer.referrer_mobile = referrer_mobile
    customer.save()

    login(request, authenticate(username=mobile, password=password))
    return HttpResponseRedirect(reverse('peggy.views.index'))


def login_page(request, msg=""):
    next_page = request.GET.get('next', default=reverse('peggy.views.index'))
    return render_to_response('peggy/login.html', {'msg': msg, 'next': next_page},
                              context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def survey(request):
    return render_to_response('peggy/survey.html',
                              {"btn2_navbar_active": "active"}
                              , context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def do_survey(request):
    answers = {}
    answers["birthday"] = request.POST.get('birthday', '1982-05-31')
    answers["gender"] = request.POST["gender"]
    answers["answer1"] = request.POST["answer1"]
    answers["answer2"] = request.POST["answer2"]
    answers["answer3"] = request.POST["answer3"]
    answers["answer4"] = request.POST["answer4"]
    answers["answer5"] = request.POST["answer5"]
    answers["answer6"] = request.POST["answer6"]
    answers["answer7"] = request.POST.getlist("answer7")
    answers["answer8"] = request.POST["answer8"]
    answers["answer9"] = request.POST["answer9"]
    answers["answer10"] = request.POST["answer10"]
    answers["answer11"] = request.POST["answer11"]
    answers["answer12"] = request.POST["answer12"]
    answers["answer13"] = request.POST["answer13"]
    answers["answer14"] = request.POST["answer14"]
    answers["answer15"] = request.POST["answer15"]
    answers["answer16"] = request.POST["answer16"]
    answers["answer17"] = request.POST["answer17"]
    answers["answer18"] = request.POST["answer18"]
    answers["answer19"] = request.POST["answer19"]
    answers["answer20"] = request.POST["answer20"]
    answers["answer21"] = request.POST["answer21"]
    answers["answer22"] = request.POST["answer22"]
    answers["answer23"] = request.POST["answer23"]
    answers["answer7ex"] = request.POST["answer7ex"]
    answers["answer14ex"] = request.POST["answer14ex"]
    answers["answer16ex"] = request.POST["answer16ex"]
    answers["answer17ex"] = request.POST["answer17ex"]
    answers["answer22ex"] = request.POST["answer22ex"]
    # print answers

    customer = request.user.customer
    customer.birthday = datetime_safe.datetime.strptime(request.POST.get('birthday', '1982-05-31'), '%Y-%m-%d')
    customer.gender = request.POST.get('gender', '')
    customer.save()

    survey_result = SurveyResult(user=request.user)
    survey_result.answers = json.dumps(answers)
    survey_result.save()

    return HttpResponseRedirect(reverse('peggy.views.products', kwargs={"survey_result_id": survey_result.id}))


@login_required(login_url=LOGIN_URL)
def products(request, survey_result_id):
    return render_to_response('peggy/products.html',
                              {'products': Product.objects.all(), 'survey_result_id': survey_result_id},
                              context_instance=RequestContext(request))


def payment_wap(request):
    survey_result_id = request.POST.get("survey_result_id")
    order = Order.objects.create(user=request.user, survey_result=SurveyResult.objects.get(pk=survey_result_id))

    total_price = 0
    product_count = int(request.POST.get("product_count", 0))
    for i in xrange(product_count):
        product = Product.objects.get(pk=request.POST.get("product_id" + str(i)))
        amount = int(request.POST.get("product_amount" + str(i)))
        # print product, amount
        if amount > 0:
            order_item = OrderItem.objects.create(order=order, product=product, amount=amount)
            total_price += product.price * amount

    order.total_price = total_price
    order.discount_price = total_price

    # ####### point rules #######
    try:
        referrer = Customer.objects.get(user__username=(request.user.customer).referrer_mobile)
        getcontext().prec = 2
        order.discount_price = total_price * Decimal(0.8)
        referrer.point += int(total_price) * 2
    except Exception, e:
        print e
    finally:
        print '========', total_price, type(total_price), order.discount_price, type(order.discount_price)
    # ###########################

    order.out_trade_no = _generate_req_seq()
    order.save()

    return HttpResponse(AlipayWap().make(order.out_trade_no, u"Peggy's实验室定制", str(order.discount_price)))


@csrf_exempt
def paid_wap(request):
    params = request.GET.dict()
    # print params
    is_correct_sign = AlipayWap().is_correct_sign(params)

    order = Order.objects.get(out_trade_no=params['out_trade_no'])
    # print order

    return render_to_response('peggy/paid.html',
                              {'out_trade_no': params["out_trade_no"], 'result': params['result'],
                               'discount_price': order.discount_price,
                               'is_correct_sign': is_correct_sign}, context_instance=RequestContext(request))


@csrf_exempt
def paid_notify_wap(request):
    params = request.POST.dict()
    verify_result = AlipayWap().notify_call(params, verify=True)
    print "ASYNC_wap verifying alipay: ", verify_result, params

    if verify_result == 'success':
        try:
            t = ET.fromstring(params['notify_data'].encode('utf8'))
            out_trade_no = t.find('out_trade_no').text
            print "change order state for ", out_trade_no
            order = Order.objects.get(out_trade_no=out_trade_no)
            order.state = Order.PAID
            order.pay_date = datetime_safe.datetime.now()
            order.save()
        except Exception, e:
            print e
    return HttpResponse(verify_result)


@login_required(login_url=LOGIN_URL)
def order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render_to_response('peggy/order.html', {'order': order, 'order_items': order_items},
                              context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def express(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    req = urllib2.urlopen(
        urllib2.quote("http://www.kuaidi100.com/query?type=%s&postid=%s" % (order.express_vendor, order.express_no),
                      safe="%/:=&?~#+!$,;'@()*[]"))
    data = json.loads(req.read().decode('utf-8'))

    return render_to_response('peggy/express.html', {'order': order, 'data': data['data']},
                              context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def mine(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render_to_response('peggy/mine.html',
                              {'orders': orders, 'customer': customer, "btn5_navbar_active": "active"},
                              context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def mine_edit(request):
    customer = get_object_or_404(Customer, user=request.user)
    return render_to_response('peggy/mine_edit.html',
                              {'customer': customer, "btn5_navbar_active": "active"},
                              context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def do_update_mine(request):
    customer = get_object_or_404(Customer, user=request.user)
    customer.first_name = request.POST['first_name']
    customer.avatar_url = request.POST['avatar_url']
    customer.address = request.POST['address']
    customer.gender = request.POST['gender']
    customer.birthday = str2d(request.POST['birthday'])
    customer.save()

    return HttpResponseRedirect(reverse('peggy.views.mine'))


def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            next_page = request.POST.get('next', '') or reverse('peggy.views.index')
            return HttpResponseRedirect(next_page)
        else:
            return render_to_response('peggy/login.html', {
                'msg': '用户被锁定',
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('peggy/login.html', {
            'msg': '用户名或密码错误',
        }, context_instance=RequestContext(request))


def do_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('peggy.views.index'))


def all_bulletins(request):
    return render_to_response('peggy/articles.html', {
        'articles': Article.objects.filter(type=Article.BULLETIN).order_by('-create_time'),
        "btn3_navbar_active": "active"},
                              context_instance=RequestContext(request))


def all_articles(request):
    return render_to_response('peggy/articles.html', {
        'articles': Article.objects.filter(type=Article.ARTICLE).order_by('-create_time'),
        "btn3_navbar_active": "active"},
                              context_instance=RequestContext(request))


def article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render_to_response('peggy/article.html', {
        'article': article}, context_instance=RequestContext(request))


@login_required(login_url=LOGIN_URL)
def do_checkin(request):
    t = datetime.now()
    today_midnight = datetime(t.year, t.month, t.day)

    customer = Customer.objects.get(user=request.user)

    if customer.last_checkin_time < today_midnight:
        customer.last_checkin_time = datetime.now()
        customer.point += 2
        customer.save()
        return restful({'last_checkin_time': dt2str(customer.last_checkin_time)})
    return restful({'last_checkin_time': dt2str(customer.last_checkin_time)}, error_code=5,
                          error_msg='already checked-in today')


def bulletin(request, article_id):
    return article(request, article_id)


@login_required(login_url=LOGIN_URL)
def do_claim_refund(request):
    customer = get_object_or_404(Customer, user=request.user)

    if customer.point > 0:
        claim = RefundClaim(user=customer.user, point=customer.point)
        claim.save()
        customer.point = 0
        customer.save()

    return HttpResponseRedirect(reverse('peggy.views.mine'))




