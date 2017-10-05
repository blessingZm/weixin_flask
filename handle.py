"""
对消息的所有处理方法！最后的信息均处理成xml格式
"""
from wx_replys.reply_event import replyEvent
from wx_replys.reply_function import replyFunction
from wx_replys.reply_forecast import replyForecast
from wx_replys.reply_rain import replyRain
from wx_replys.reply_tulin import replyTulin
from wx_replys.reply_imginfo import replyImginfo
from wx_replys.reply_forecast_ZNweather import replyForecastChina
from wechatpy.replies import TextReply, ArticlesReply

def Post(receiveXml):
    userid = receiveXml.source[0: 15]
    # 消息推送
    if receiveXml.type == 'event':
        Event = receiveXml.event
        replyMsg = replyEvent(receiveXml, Event)

    # 针对不同文本消息的回复
    elif receiveXml.type == 'text' or receiveXml.type == 'voice':
        if receiveXml.type == 'text':
            content = receiveXml.content
        else:
            content = receiveXml.recognition.replace('。', '')
        print(content)
        if content == '功能':
            replyMsg = replyFunction()
        elif content.endswith('天气'):
            replyMsg = replyForecast(content)
        elif content.startswith('天气'):
            replyMsg = replyForecastChina(content).getWeather()
        elif content.endswith('雨量'):
            replyMsg = replyRain(content).getRain()
        else:
            replyMsg = replyTulin(content, userid)

    # 对人物图片消息的处理
    elif receiveXml.type == 'image':
        picUrl = receiveXml.image
        replyMsg = replyImginfo(picUrl)
    else:
        replyMsg = "无法识别，请见谅！"

    if not isinstance(replyMsg, list):
        reply = TextReply(content='{}'.format(replyMsg), message=receiveXml)
    else:
        reply = ArticlesReply(message=receiveXml, articles=replyMsg)
    # 转换成 XML
    replyXml = reply.render()
    return replyXml
