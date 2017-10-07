# -*- coding: utf-8 -*-
# 利用图灵机器人自动聊天
import requests
import json


def replyTulin(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None

    content, is_replay = yield ('TextMsg', '当前为机器人聊天模式，，需要退出机器人聊天模式时请输入：9\n\n'
                                           '开始随便聊聊吧....')
    while True:
        if content == '9':
            return ('TextMsg', '退出机器人聊天模式，开始新的会话模式请输入对应的数字进入！')
        else:
            s = requests.session()
            url = 'http://www.tuling123.com/openapi/api'
            da = {"key": "6863cff9d93e4a6bbcd03f004f566a8a",
                  "info": content,
                  "userid": to_user[0: 15]}
            data = json.dumps(da)
            r = s.post(url, data=data)
            j = eval(r.text)
            code = j['code']
            if code == 100000:
                msg = j['text']
            elif code == 200000:
                msg = j['text']+j['url']
            elif code == 302000:
                msg = j['text']+j['list'][0]['info']+j['list'][0]['detailurl']
            elif code == 308000:
                msg = j['text']+j['list'][0]['info']+j['list'][0]['detailurl']
            else:
                msg = '对不起，我不明白这句话！'
            content, is_replay = yield ('TextMsg', msg)
