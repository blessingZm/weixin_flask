# -*- coding: utf-8 -*-
"""根据“地区+天气”，利用天气预报api接口获取5天预报"""
import requests


def replyForecast(content):
    location = content.replace('天气', '')
    s = requests.session()
    weathers = []
    url = 'http://wthrcdn.etouch.cn/weather_mini?city={}'.format(location)
    res = s.get(url)
    content = res.content
    try:
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
        return msg
    except:
        return '未查询到地名：{},请重新查询！'.format(location)

