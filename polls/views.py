#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from polls.models import Poll, Choice
import json
import hashlib, time, re, urllib2, urllib
from xml.etree import ElementTree as ET
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt


def jsonp(request):
    return HttpResponse(json.dumps([1,2,3,4,5, None, True]), content_type="application/json")

######### WeiXin #########################

WEIXIN_TOKEN = "JACKY"

#测试号
# APP_ID= 'wx62b78e3d97080e93'
# APP_SECRET = '3483543989f61c07bdd7f5bcff3eb9d3'

#天津软件沙龙
# APP_ID= 'wxfa590ca25889e839'
# APP_SECRET = 'd86a513fc25ba967364cfa4cb4ba3e00'

#17运动网
APP_ID= 'wx6b8d8dff23e4d723'
APP_SECRET = 'b503198f1f0d5e24d89727d3a1541960'

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

IMAGE_TMPL = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[%s]]></MediaId>
</Image>
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
        signature = request.GET.get("signature", 'null')
        timestamp = request.GET.get("timestamp", 'null')
        nonce = request.GET.get("nonce", 'null')
        echostr = request.GET.get("echostr", 'null')
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = hashlib.sha1("".join(tmp_list)).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin main (signature wrong)")
    else:   ### POST
        return _post_msg_dispatch(request)


def _post_msg_dispatch(request):
    xml_str = smart_str(request.body)
    xml = ET.fromstring(xml_str)
    print xml_str

    msgType = xml.find("MsgType").text
    fromUserName = xml.find("ToUserName").text
    toUserName = xml.find("FromUserName").text
    postTime = str(int(time.time()))

    generics = (fromUserName, toUserName, postTime)

    if msgType == 'text':
        return _reply_text_msg(xml, *generics)
    elif msgType == 'image':
        return _reply_image_msg(xml, *generics)
    elif msgType == 'event':
        return _reply_event_msg(xml, *generics)
    elif msgType == 'location':
        return _reply_location_msg(xml, *generics)
    else:
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, "无法识别的命令交互类型 <%s>..." % msgType))


def _reply_text_msg(xml, fromUserName, toUserName, postTime):
    msgId = xml.find("MsgId").text
    content = xml.find("Content").text
    print content

    if content == 't':
        r = REPLY_TMPL % (toUserName, fromUserName, postTime, _get_access_token())
    elif content == 'n':
        r = REPLY_TMPL % (toUserName, fromUserName, postTime, _create_menu())
    elif content == 'm':
        r = MUSIC_TMPL % (toUserName, fromUserName, postTime, 
            "当你老了", "莫文蔚+申健", 'http://yinyueshiting.baidu.com/data2/music/137081688/137078183169200128.mp3?xcode=3f8daaf15d85ed8badcbb9aec74595eb0b86fc0e5b731aec', 'http://yinyueshiting.baidu.com/data2/music/137081688/137078183169200128.mp3?xcode=3f8daaf15d85ed8badcbb9aec74595eb0b86fc0e5b731aec', '8mtENBlNa2hjiGvHzCOUMSrAR0bpAthOX7Un_dE2BZQipzR_O6BB3amcjGbViqwb')
    elif content == 'i':
        r = IMAGE_TMPL % (toUserName, fromUserName, postTime, 'Wl1XX2zhwkMhULxD_JnKPuaq64XUPxLB9C2HTleBxAiKV1C2oCEdp6IvZlHYVxOD')
    else:
        r = REPLY_TMPL % (toUserName, fromUserName, postTime, "无法识别的文本交互... %s" %(smart_str(content)))

    print r
    return HttpResponse(r)

def _reply_location_msg(xml, fromUserName, toUserName, postTime):
    x = xml.find("Location_X").text
    y = xml.find("Location_Y").text
    scale = xml.find("Scale").text
    label = xml.find("Label").text
    return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
        "你在(%s,%s)@%s-%s" % (x, y, scale, smart_str(label))))

def _reply_image_msg(xml, fromUserName, toUserName, postTime):
    picUrl = xml.find("PicUrl").text
    mediaId = xml.find("MediaId").text
    return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
        "暂不支持识别图片交互哦,功能开发中... %s , %s" % (picUrl, mediaId)))


def _reply_event_msg(xml, fromUserName, toUserName, postTime):
    event = xml.find("Event").text

    if event == 'LOCATION':
        latitude = xml.find("Latitude").text
        longitude = xml.find("Longitude").text
        precision = xml.find("Precision").text
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "你的坐标(%s,%s)@%s" % (latitude, latitude, precision)))
    elif event == 'subscribe':
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "欢迎订阅"))
    elif event == 'ENTER':
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "欢迎回来"))
    elif event == 'scancode_waitmsg' or event == 'scancode_push':
        eventKey = xml.find("EventKey").text
        scanType = xml.find("ScanCodeInfo/ScanType").text
        scanResult = xml.find("ScanCodeInfo/ScanResult").text
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "扫一扫成功 %s %s %s" % (eventKey, scanType, scanResult) ))
    elif event == 'CLICK':
        eventKey = xml.find("EventKey").text
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "你点击了菜单 eventKey=%s" % (eventKey)))
    else:
        return HttpResponse(REPLY_TMPL % (toUserName, fromUserName, postTime, 
            "暂不支持识别事件交互哦,功能开发中... %s" % (event)))


def _get_access_token():
    """
    7200s有效，需要全局缓存下来
    """
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APP_ID, APP_SECRET)
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    json_str = req.read()
    return json.loads(json_str).get('access_token')

def _get_jsapi_ticket():
    """
    7200s有效，需要全局缓存下来
    """
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (_get_access_token())
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    json_str = req.read()
    return json.loads(json_str).get('ticket')


def _create_menu():
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % _get_access_token()
    body = {
    "button": [
        {
            "type": "view", 
            "name": 'HOME', 
            "url": "http://123.57.88.24/polls/"
        }, 
        {
            "name": "L", 
            "type": "location_select", 
            "key": "rselfmenu_2_0"
        }, 
        {
            "name": "M", 
            "sub_button": [
                {
                    "type": "scancode_waitmsg", 
                    "name": "SCAN", 
                    "key": "rselfmenu_0_0", 
                    "sub_button": [ ]
                }, 
                {
                    "type": "view", 
                    "name": "S", 
                    "url": "http://www.soso.com/"
                }, 
                {
                    "type": "click", 
                    "name": "tap me", 
                    "key": "V1001_TODAY_MUSIC"
                }, 
                {
                    "type": "pic_photo_or_album", 
                    "name": "P", 
                    "key": "rselfmenu_1_1"
                }]
        }]
    }

    post_json_str = json.dumps(body, ensure_ascii=False)
    # post_json_str = urllib.urlencode(body)
    print post_json_str, type(post_json_str), urllib2.quote(post_json_str)
    req = urllib2.urlopen(urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]"), post_json_str)
    json_str = req.read()
    print json_str
    return json.loads(json_str).get('errmsg')


#############################

def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    timestamp = int(time.time())
    noncestr = 'NONCE'
    url = 'http://123.57.88.24/polls/'
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (_get_jsapi_ticket(), noncestr, timestamp, url)
    return render_to_response('polls/index.html', {'latest_poll_list': latest_poll_list,
        'appId': APP_ID, 'timestamp': timestamp, 'nonceStr': noncestr, 
        'signature': hashlib.sha1(s).hexdigest(), 's': s})

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
