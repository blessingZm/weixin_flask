# -*- coding: utf-8 -*-
"""
handle.Post为消息处理函数
"""
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from flask import Flask, request, make_response
from handle import Post

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello():
    return "Hello World"


@app.route('/wx', methods=['GET', 'POST'])
def we_chat():
    if request.method == 'GET':
        # 获取输入参数
        data = request.args
        signature = data.get('signature')
        timestamp = data.get('timestamp')
        nonce = data.get('nonce')
        echostr = data.get('echostr')
        # 自己的token
        token = "blessingWx"  # 这里改写你在微信公众平台里输入的token
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException as e:
            print(e)
        else:
            return make_response(echostr)
    else:
        # 获取接收的信息
        # 接收的xml数据，用于获取wechatpy解析后不包含的内容
        rec = request.stream.read()
        # wechatpy解析后的数据，用于wechatpy的消息回复
        msg = parse_message(rec)
        # 用户id
        userid = msg.source[0: 15]
        # 取得解析信息后准备传回的xml信息
        xml = Post(rec, msg, userid)
        return make_response(xml)


if __name__ == '__main__':
    app.run()
