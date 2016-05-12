# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponse, HttpResponseBadRequest
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
import sys
from wechat_sdk.messages import TextMessage
from wechat_sdk.messages import VoiceMessage
from wechat_sdk.messages import EventMessage
from wechat import WeixinPublic
import MySQLdb
import projectoxord as po
import json
import urllib, urllib2


def HandleSql(sql, ret):
    db = MySQLdb.connect("localhost", "root", "a7641368", "smartlock",
                         charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        # print sql
        if ret == 'yes':
            return cursor.fetchall()
    except:
        db.rollback()
    finally:
        db.close()


reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')
conf = WechatConf(
    token='smartlock',
    appid='wxfcefecd762600918',
    appsecret='b1c545a1800229e29266c02cb5161dbc',
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='8mZ2qm5hVKI14AFrKEYlhxcUyh2YhdyebnVzt1mQEwy'  # 如果传入此值则必须保证同时传入 token, appid
)
wechat = WechatBasic(conf=conf)


def index(request):
    return HttpResponse("Hello world!")


# Create your views here.
def wechat_handle(request):
    if request.method == 'GET':
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        if wechat.check_signature(signature, timestamp, nonce):
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin  index")
    try:
        wechat.parse_data(request.body)
    except ParseError:
        print 'Invalid Body Text'
    id = wechat.message.id  # 对应于 XML 中的 MsgId
    target = wechat.message.target  # 对应于 XML 中的 ToUserName
    source = wechat.message.source  # 对应于 XML 中的 FromUserName
    time = wechat.message.time  # 对应于 XML 中的 CreateTime
    type = wechat.message.type  # 对应于 XML 中的 MsgType
    if isinstance(wechat.message, TextMessage):
        content = wechat.message.content
        if content.startswith("绑定"):
            list = content.split('+')
            cid = list[1]
            cpass = list[2]
            weixin = WeixinPublic("chaopengz1993@gmail.com", "a7641368")
            fakeid, name = weixin.get_msg_list()
            sql = "update user SET fakeid = '" + fakeid + "' where cid ='" + cid + "' AND cpass = '" + cpass + "'"
            HandleSql(sql, ret='no')
            xml = wechat.response_text(content='绑定成功！')
        elif content.startswith('开门'):
            response = opendoor()
            if response == "open door!":
                xml = wechat.response_text(content="开门成功")
            else:
                xml = wechat.response_text(content=response)
        elif content.startswith('详情'):
            xml = detail()
        elif content.startswith("他是"):
            sql = "SELECT * FROM  vistors ORDER BY id DESC LIMIT 1"
            lines = HandleSql(sql, "yes")
            name = content[2:]
            for line in lines:
                sid = line[0]
                simgurl = line[2]
            sql = "update vistors SET vname = '" + name + "' where id =" + str(sid) + ";"
            HandleSql(sql, "no")
            if po.createPeople(name, simgurl) == "createSuccess":
                xml = wechat.response_text(content="标记成功。\n下次来访将自动为您识别该用户姓名。")
            else:
                xml = wechat.response_text(content="抱歉，未在图片中识别出人脸。")
        else:
            xml = wechat.response_text(content="抱歉，没明白您的指令！")
        return HttpResponse(xml)

    if isinstance(wechat.message, VoiceMessage):
        text = wechat.message.recognition
        if text.startswith('开门'):
            response = opendoor()
            if response == "open door!":
                xml = wechat.response_text(content="开门成功")
            else:
                xml = wechat.response_text(content=response)
        elif text.startswith('详情'):
            xml = detail()
        else:
            ret = "抱歉。没识别您的指令。\n您说的是：" + text
            xml = wechat.response_text(content=ret)
        return HttpResponse(xml)

    if isinstance(wechat.message, EventMessage):
        if wechat.message.type == 'click':
            if wechat.message.key == 'detail':
                xml = detail()
            elif wechat.message.key == 'opendoor':
                response = opendoor()
                if response == "open door!":
                    xml = wechat.response_text(content="开门成功")
                else:
                    xml = wechat.response_text(content=response)
        else:
            ret = 'error'
            xml = wechat.response_text(content=ret)
        return HttpResponse(xml)


def towechat(request):
    pname = '陌生人'
    imgurl = ''
    time = ''
    if request.method == 'POST':
        # cid = request.POST['cid']
        imgurl = request.POST['url']
        time = request.POST['time']
    sql = "select fakeid from user where cid = 'buaa001';"  # + cid + "';"
    lines = HandleSql(sql, ret='yes')
    for line in lines:
        fakeid = line[0]
    print imgurl
    pname = po.getWho(url=imgurl)
    print pname
    weixin = WeixinPublic("chaopengz1993@gmail.com", "a7641368")
    text = '主人，『' + pname + '』来啦。\n\n\n如若立即开门回复<开门>\n查看具体信息回复<详情>'
    sql = "insert into vistors (vname,imgurl,vtime) VALUES ('" + pname + "','" + imgurl + "','" + time + "');"
    HandleSql(sql, "no")
    print fakeid
    weixin.sendMessage(text, fakeid)
    return HttpResponse("ok.imgurl = %s" % pname)


def login(request):
    cid = ''
    cpass = ''
    token = ''
    if request.method == 'POST':
        cid = request.POST['cid']
        cpass = request.POST['cpass']
        token = request.POST['token']
    sql = "select cpass from user WHERE cid = '" + cid + "';"
    lines = HandleSql(sql, ret='yes')
    print sql, lines
    for line in lines:
        if line[0] != cpass:
            return HttpResponse("error")
        else:
            sql = "update user set token = '" + token + "'where cid = '" + cid + "';"
            HandleSql(sql, 'no')
            return HttpResponse("ok")
    return HttpResponse("error")


def getHistory(request):
    sql = "SELECT * FROM  vistors ORDER BY id DESC LIMIT 5"
    lines = HandleSql(sql, 'yes')
    list = []
    for line in lines:
        id = line[0]
        name = line[1]
        imgurl = line[2]
        time = line[3]
        d = dict(id=id, name=name, imgurl=imgurl, time=time)
        list.append(d)
    return HttpResponse(json.dumps(list, ensure_ascii=False, indent=2))


def opendoor():
    values = {"instruction": 'yes'}
    data = urllib.urlencode(values)
    url = "http://chaopengz.nat123.net:19870/open/"
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)
    return response.read()


def create(request):
    dict = {
        'button': [
            {
                'type': 'click',
                'name': '开门',
                'key': 'opendoor'
            },
            {
                'type': 'click',
                'name': '详情',
                'key': 'detail'
            },
            # {
            #     'type': 'view',
            #     'name': '监控',
            #     'url': 'http://www.baidu.com'
            # },
        ]
    }
    wechat.create_menu(dict)
    return HttpResponse("Create success!")


def detail():
    sql = "SELECT * FROM  vistors ORDER BY id DESC LIMIT 1"
    lines = HandleSql(sql, "yes")
    for line in lines:
        sid = line[0]
        svname = line[1]
        simgurl = line[2]
        stime = line[3]
        xml = wechat.response_news([
            {
                'title': svname + '  来啦',
                'description': '来访时间： ' + stime,
                'picurl': simgurl,
                'url': simgurl,
            }
        ])
    return xml


    # po.createPeople("兵长","http://xlock.chaopengz.com/2016-05-07,14:56:50.jpg")
