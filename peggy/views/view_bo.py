#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import datetime_safe
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from xml.etree import ElementTree as ET

from decorators import staff_only
from peggy.models import *
from peggy.lib.alipaylib import AlipayWap
from peggy.lib import django_qiniu
from utils import *

BO_LOGIN_URL = "/peggy/bo_login_page"
DEFAULT_PAGE_SIZE = 10


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def bo_index(request):
    try:
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', DEFAULT_PAGE_SIZE))
    except ValueError:
        page = 1
        size = DEFAULT_PAGE_SIZE

    paginator = Paginator(Order.objects.all().order_by('-create_time'), size)

    try:
        orders = paginator.page(page)
    except (EmptyPage, InvalidPage):
        orders = paginator.page(paginator.num_pages)

    return render_to_response('peggy/bo_index.html',
                              {'orders': orders, 'page_range': paginator.page_range, 'size': size},
                              context_instance=RequestContext(request))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def bo_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render_to_response('peggy/bo_order.html', {'order': order, 'order_items': order.orderitem_set.all()},
                              context_instance=RequestContext(request))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def do_bo_update_order(request, order_id):
    express_no = request.POST['express_no']
    express_vendor = request.POST['express_vendor']

    order = get_object_or_404(Order, id=order_id)
    order.express_no = express_no
    order.express_vendor = express_vendor
    order.deliver_date = datetime_safe.datetime.now()
    order.save()

    return HttpResponseRedirect(reverse('peggy.views.bo_order', kwargs={'order_id': order.id}))


def bo_login_page(request, msg=""):
    next_page = request.GET.get('next', default=reverse('peggy.views.bo_index'))
    return render_to_response('peggy/bo_login.html', {'msg': msg, 'next': next_page},
                              context_instance=RequestContext(request))


def do_bo_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if not user.is_staff:
            return render_to_response('peggy/bo_login.html', {
                'msg': '用户无管理员权限',
            }, context_instance=RequestContext(request))
        elif user.is_active:
            login(request, user)
            # Redirect to a success page.
            next_page = request.POST.get('next', '') or reverse('peggy.views.bo_index')
            return HttpResponseRedirect(next_page)
        else:
            return render_to_response('peggy/bo_login.html', {
                'msg': '用户被锁定',
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('peggy/bo_login.html', {
            'msg': '用户名或密码错误',
        }, context_instance=RequestContext(request))


def do_bo_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('peggy.views.bo_index'))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def bo_refund_claims(request):
    try:
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', DEFAULT_PAGE_SIZE))
    except ValueError:
        page = 1
        size = DEFAULT_PAGE_SIZE

    paginator = Paginator(RefundClaim.objects.all().order_by('-create_time'), size)

    try:
        refund_claims = paginator.page(page)
    except (EmptyPage, InvalidPage):
        refund_claims = paginator.page(paginator.num_pages)

    return render_to_response('peggy/bo_refund_claims.html', {
        'refund_claims': refund_claims, 'page_range': paginator.page_range, 'size': size},
        context_instance=RequestContext(request))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def do_bo_refund(request, claim_id):
    claim = get_object_or_404(RefundClaim, pk=claim_id)
    claim.state = RefundClaim.REFUNDED
    claim.refund_date = datetime.now()
    claim.save()
    return HttpResponseRedirect(reverse('peggy.views.bo_refund_claims'))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def bo_all_articles(request):
    try:
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', DEFAULT_PAGE_SIZE))
    except ValueError:
        page = 1
        size = DEFAULT_PAGE_SIZE

    paginator = Paginator(Article.objects.all().order_by('-create_time'), size)

    try:
        articles = paginator.page(page)
    except (EmptyPage, InvalidPage):
        articles = paginator.page(paginator.num_pages)

    return render_to_response('peggy/bo_articles.html', {
        'articles': articles, 'page_range': paginator.page_range, 'size': size},
                              context_instance=RequestContext(request))


@login_required(login_url=BO_LOGIN_URL)
@staff_only(redirect_url=BO_LOGIN_URL)
def bo_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.title = request.POST['title']
        article.cover_img_url = request.POST['cover_img_url']
        article.text = request.POST['text']
        article.type = request.POST['type']
        article.save()
        return HttpResponseRedirect(reverse('peggy.views.bo_article', kwargs={'article_id': article_id}))
    else:
        return render_to_response('peggy/bo_article.html', {
            'article': article}, context_instance=RequestContext(request))
