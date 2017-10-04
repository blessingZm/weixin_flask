# -*- coding: utf-8 -*-
# 利用图灵机器人自动聊天
import requests
import json
from wechatpy.replies import TextReply


def replyTulin(receivemsg, content, userid):
    s = requests.session()
    url = 'http://www.tuling123.com/openapi/api'
    da = {"key": "6863cff9d93e4a6bbcd03f004f566a8a",
          "info": content,
          "userid": userid}
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

    # 数据转为可回复的xml格式
    reply = TextReply(content='{}'.format(msg), message=receivemsg)
    # 转换成 XML
    xml = reply.render()
    return xml