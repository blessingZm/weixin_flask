# -*- coding: utf-8 -*-
"""利用天气预报api接口获取5天预报"""
import requests
import re

re_str = re.compile('^([\u4e00-\u9fa5]+)\s*天气$')


def get_weather(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None

    location = re_str.findall(receiveData)[0]
    s = requests.session()
    weathers = []
    url = 'http://wthrcdn.etouch.cn/weather_mini?city={}'.format(location)
    try:
        res = s.get(url)
        content = res.content
        headTxt = '{}——未来5天天气预报'.format(eval(content)['data']['city'])
        weathers.append(headTxt)
        datas = eval(content)['data']['forecast']
    except:
        msg_content = '未查询到地区：{}'.format(location)
    else:
        for data in datas:
            date = data['date']
            dayType = data['type']
            lowT = data['low'].split(' ')[-1]
            highT = data['high'].split(' ')[-1]
            dayWeather = ' '.join([date, dayType, lowT, '--', highT])
            weathers.append(dayWeather)
        msg_content = str('\n'.join(weathers))
    return ('TextMsg', msg_content)
