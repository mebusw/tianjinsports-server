#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from polls.models import Poll, Choice
import json
import hashlib, time, re, urllib2
from xml.etree import ElementTree as ET
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt


def jsonp(request):
    return HttpResponse(json.dumps([1,2,3,4,5, None, True]), content_type="application/json")

######### WeiXin #########################

WEIXIN_TOKEN = "JACKY"
APP_ID= 'wx62b78e3d97080e93'
APP_SECRET = '3483543989f61c07bdd7f5bcff3eb9d3'
REPLY_TMPL = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
            </xml>"""

MUSIC_TMPL = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[music]]></MsgType>
<Music>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<MusicUrl><![CDATA[%s]]></MusicUrl>
<HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
<ThumbMediaId><![CDATA[%s]]></ThumbMediaId>
</Music>
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
        tmp_str = hashlib.sha1("".join(tmp_list)).hexdigest()
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
        elif content == "access_token":
            return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, _get_access_token()))
        elif content == 'music':
            return HttpResponse(MUSIC_TMPL % (toUserName, fromUserName, postTime, 
                "当你老了", "莫文蔚+申健", 'http://yinyueshiting.baidu.com/data2/music/137081688/137078183169200128.mp3?xcode=3f8daaf15d85ed8badcbb9aec74595eb0b86fc0e5b731aec', '', '8mtENBlNa2hjiGvHzCOUMSrAR0bpAthOX7Un_dE2BZQipzR_O6BB3amcjGbViqwb'))
        else:
            return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, "暂不支持任何命令交互哦,功能开发中..."))
        response_xml = WEIXIN_REPLY_TMPL
        return HttpResponse(response_xml)


def _get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APP_ID, APP_SECRET)
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    json_str = req.read().decode('utf-8')
    return json_str

#############################

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
