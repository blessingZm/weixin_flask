# -*- coding: utf-8 -*-
"""根据“地区+天气”，利用天气预报api接口获取5天预报"""
import requests
from wechatpy.replies import TextReply


def replyForecast(receivemsg):
    location = receivemsg.content.replace('天气', '')
    s = requests.session()
    weathers = []
    url = 'http://wthrcdn.etouch.cn/weather_mini?city={}'.format(location)
    res = s.get(url)
    content = res.content
    headTxt = '{}——未来5天天气预报'.format(eval(content)['data']['city'])
    weathers.append(headTxt)
    datas = eval(content)['data']['forecast']

    for data in datas:
        date = data['date']
        dayType = data['type']
        lowT = data['low'].split(' ')[-1]
        highT = data['high'].split(' ')[-1]
        dayWeather = ' '.join([date, dayType, lowT, '--', highT])
        weathers.append(dayWeather)
    msg = str('\n'.join(weathers))
    # 数据转为可回复的xml格式
    reply = TextReply(content='{}'.format(msg), message=receivemsg)
    # 转换成 XML
    xml = reply.render()
    return xml
