"""
demo_server, demo_dialog, wechat/, demo_dialog_reply/
实现根据上下文对话，主要模块在wechat/, 处理函数在demo_dialog_reply/
"""

import logging
import hashlib

from flask import Flask, request

import wechat.bot
import demo_dialog

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.debug = True

# 公众号token
TOKEN = 'blessingWx'
        
@app.route('/wx', methods=['GET'])
def wechat_get():
    timestamp = request.args.get('timestamp', '')
    if not timestamp:
        return 'This page is used for wechat validation'
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    token = TOKEN
    
    list = [token, timestamp, nonce]
    list.sort()
    list = ''.join(list).encode('utf-8')
    logger.debug(list)
    hashcode = hashlib.sha1(list).hexdigest()
    logger.info('handle/GET func: hashcode %s, signature %s' % (hashcode, signature))
    if hashcode == signature:
        return echostr
    else:
        return ''
        
@app.route('/wx', methods=['POST'])
def wechat_post():
    data = request.get_data()
    logger.info('Receiving data: %s' % data)
    return wechat.bot.answer(data, demo_dialog).format()
            

if __name__ == '__main__':
    app.run(port=5000)
