"""
对消息的所有处理方法！最后的信息均处理成xml格式
"""

import xml.etree.ElementTree as ET
from wx_replys.reply_event import replyEvent
from wx_replys.reply_function import replyFunction
from wx_replys.reply_forecast import replyForecast
from wx_replys.reply_rain import replyRain
from wx_replys.reply_tulin import replyTulin
from wx_replys.reply_imginfo import replyImginfo
from wx_replys.reply_wetherPic import replyWetherPic
from wx_replys.reply_forecastPic import replyForecastPic
from wx_replys.reply_forecast_ZNweather import replyForecastChina
from wechatpy.replies import TextReply

def Post(rec, msg, userid):
    # 消息推送
    if msg.type == 'event':
        xml = replyEvent(msg)
    # 针对不同文本消息的回复
    elif msg.type == 'text':
        content = msg.content
        if content == '功能':
            xml = replyFunction(msg)
        elif content.endswith('天气'):
            xml = replyForecast(msg)
        elif content.startswith('天气'):
            xml = replyForecastChina(msg).replyMsg()
        elif content.endswith('雨量'):
            xml = replyRain(msg).replyMsg()
        elif content.startswith('天气图'):
            xml = replyWetherPic(msg).replyMsg()
        elif content.startswith('数值预报'):
            xml = replyForecastPic(msg).replyMsg()
        else:
            xml = replyTulin(msg, content, userid)
    # 针对语音消息的回复
    elif msg.type == 'voice':
        content = msg.recognition
        xml = replyTulin(msg, content, userid)
    # 针对图片消息的回复
    elif msg.type == 'image':
        picurl = ET.fromstring(rec).find('PicUrl').text
        xml = replyImginfo(msg, picurl)
    else:
        reply_msg = "无法识别，请见谅！"
        reply = TextReply(content='{}'.format(reply_msg), message=msg)
        # 转换成 XML
        xml = reply.render()
    return xml
