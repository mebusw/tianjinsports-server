#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from polls.models import Poll, Choice
import json
import hashlib, time, re
from xml.etree import ElementTree as ET
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt


def jsonp(request):
    return HttpResponse(json.dumps([1,2,3,4,5, None, True]), content_type="application/json")


WEIXIN_TOKEN = "JACKY"
REPLY_TMPL = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
            </xml>"""

@csrf_exempt
def wx_main(request):
    """
    所有的消息都会先进入这个函数进行处理，函数包含两个功能，
    微信接入验证是GET方法，
    微信正常的收发消息是用POST方法。
    """
    print request.method, request.path, request.GET, request.POST
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin main (signature wrong)")
    else:   ### POST
        xml_str = smart_str(request.body)
        print xml_str
        xml = ET.fromstring(xml_str)
        content = xml.find("Content").text
        fromUserName = xml.find("ToUserName").text
        toUserName = xml.find("FromUserName").text
        postTime = str(int(time.time()))
        if not content:
            return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, "输入点命令吧...http://chajidian.sinaapp.com/ "))
        if content == "Hello2BizUser":
            return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, "查询成绩绩点请到http://chajidian.sinaapp.com/ 本微信更多功能开发中..."))
        else:
            return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, "暂不支持任何命令交互哦,功能开发中..."))
        response_xml = WEIXIN_REPLY_TMPL
        return HttpResponse(response_xml)


def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    return render_to_response('polls/index.html', {'latest_poll_list': latest_poll_list})

def detail(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('polls/detail.html', {'poll': p},
                               context_instance=RequestContext(request))

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render_to_response('polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        }, context_instance=RequestContext(request))
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls.views.results', args=(p.id,)))

def results(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('polls/results.html', {'poll': p})
