#!/usr/bin/env python
# coding: UTF-8
import json
import hashlib
import re
import random
import requests
import logging

DEBUG_LEVEL = logging.DEBUG
try:
    import colorizing_stream_handler

    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(colorizing_stream_handler.ColorizingStreamHandler())
except Exception, e:
    print 'can not import colorizing_stream_handler, using logging.StreamHandler()'
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(logging.StreamHandler())

'''base exception class.
'''


class WeixinPublicError(Exception):
    pass


'''raise when cookies expired.
'''


class WeixinNeedLoginError(WeixinPublicError):
    pass


'''rasie when unenable to login.
'''


class WeixinLoginError(WeixinPublicError):
    pass


class WeixinPublic(object):
    def __init__(self, account, pwd, token=None, cookies=None, ifencodepwd=False):
        self.account = account
        if ifencodepwd:
            self.pwd = pwd
        else:
            self.pwd = hashlib.md5(pwd).hexdigest()
        self.wx_cookies = cookies
        self.lastmsgid = 0
        self.token = token

        if self.token == None or self.wx_cookies == None:
            self.token = ''
            self.wx_cookies = ''
            self.login()

    '''login to weichat, get token and cookies.

    Raise:
        WeixinLoginError, when can not get token from respond.
    '''

    def login(self):
        url = 'https://mp.weixin.qq.com/cgi-bin/login'
        payload = {
            'username': self.account,
            'imgcode': '',
            'f': 'json',
            'pwd': self.pwd,
        }
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            # 'referer': 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN',
            'referer': 'https://mp.weixin.qq.com/',
        }

        r = requests.post(url, data=payload, headers=headers)

        logging.info('------login------')
        logging.debug("respond:\t%s" % r.text)

        s = re.search(r'token=(\d+)', r.text)
        if not s:
            logging.error('Login Error!!!')
            raise Exception("Login error.")
        self.token = int(s.group(1))
        logging.debug('token:\t%d' % self.token)

        self.wx_cookies = ''
        for cookie in r.cookies:
            self.wx_cookies += cookie.name + '=' + cookie.value + ';'
        logging.debug('cookies:\t%s' % self.wx_cookies)
        logging.info('------end login------')

    '''get message list.

    raise:
        WeixinNeedLoginError, when need re-login.

    returns:
        messages in dict.
    '''

    def get_msg_list(self):
        logging.info('------get_msg_list------')
        url = 'https://mp.weixin.qq.com/cgi-bin/message?t=message/list&token=%s&count=20&day=7' % self.token
        payload = {
            't': 'message/list',
            'token': self.token,
            'count': 20,
            'day': 7,
        }
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            'referer': 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN',
            'cookie': self.wx_cookies,
        }

        r = requests.get(url, data=payload, headers=headers)

        c = "".join(r.text.split())
        s = re.search(r'list:\((.*)\).msg_item', c)
        if s == None:
            logging.error('need re-login')
            self.login()
            raise WeixinNeedLoginError('need re-login')
        else:
            msg_list = s.group(1)
        logging.debug('msg_list:\t%s' % msg_list)
        pattern = re.compile(r'"msg_item".*?"fakeid":"(.*?)","nick_name":"(.*?)","', re.S)
        items = re.findall(pattern, msg_list)
        fakeid = items[0][0]
        name = items[0][1]
        print fakeid, name
        return fakeid, name

    def check(self):
        print self.token
        print self.wx_cookies

    def sendMessage(self, message, fakeid):
        url = 'https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json&token=' + str(
            self.token) + '&lang=zh_CN'
        payload = {
            'ajax': 1,
            'content': message,
            'f': 'json',
            'imgcode': '',
            'lang': 'zh_CN',
            'random': random.uniform(0, 1),
            'tofakeid': fakeid,
            'token': self.token,
            'type': 1
        }
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            'referer': 'https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&tofakeid=' + fakeid + '&token=' + str(
                self.token) + '&lang=zh_CN',
            'cookie': self.wx_cookies,
        }

        r = requests.post(url, data=payload, headers=headers)

        print r.text
