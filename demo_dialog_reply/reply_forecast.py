# -*- coding: utf-8 -*-
"""根据“地区+天气”，利用天气预报api接口获取5天预报"""
import requests


def replyForecast(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None
    location, is_replay = yield ('TextMsg', '当前为天气查询模式，需要退出天气查询模式时请输入：9'
                                            '\n\n请输入要查询的城市：')
    while True:
        if location == '9':
            return ('TextMsg', '退出天气预报查询模式，'
                               '开始新的会话模式请输入对应的数字进入！')
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
            location, is_replay = yield ('TextMsg', msg + '\n\n退出天气查询请输入：9\n'
                                                          '继续查询请输入要查询的城市：')
        except:
            location, is_replay = yield ('TextMsg', '未查询到城市{}!\n'
                                                    '请重新输入要查询的城市：'.format(location))
