# -*- coding: utf-8 -*-
"""根据地区从湖北业务内网5分钟雨量下载小时内雨量"""
import requests
import sqlite3
from datetime import datetime, timedelta


def get_time():
    nowTime = datetime.today()
    if nowTime.minute % 5 == 0:
        nowTime = nowTime - timedelta(minutes=1)

    bufminute = str(nowTime.minute // 5 * 5)
    if len(bufminute) == 0:
        bufminute = '0' + bufminute

    endTime = '{0}:{1}:00'.format(nowTime.strftime('%Y-%m-%d %H'), bufminute)
    if nowTime.minute // 5 == 0:
        minutes = 60
    else:
        minutes = nowTime.minute // 5 * 5
    return endTime, minutes

def get_code(country):
    if country == '9':
        return country
    else:
        dbName = 'coding.db'
        tableName = 'coding'
        db = sqlite3.connect(dbName)
        cursor = db.cursor()
        db_command = "select id from {} where address like '%{}%'".format(tableName, country)
        cursor.execute(db_command)
        code = cursor.fetchone()[0]
        return code

def down_r(code, end_time, minutes):
    stDatas = {}
    url = 'http://10.104.235.5/hbzd/hbase'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/56.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Content-Length": "476",
        "Cookie": "JSESSIONID=89DE781225AEB29CA746F9A09336E36D",
        "Connection": "keep-alive"
    }
    data = {
        'sql': "select STATIONNAME,t1.STATIONNUM STATIONNUM,PROVINCE,CITY,COUNTY,"
               "LATITUDE,LONGITUDE,ALTITUDE,SUMPRE from sta_info_reg t1,"
               "( SELECT STATIONNUM,PRE_1H SUMPRE FROM SURF_DATA_REG WHERE "
               "OBSERVTIMES = to_date('{}','yyyy-MM-dd HH:mm:ss')  "
               "and PROVINCE='湖北省' and ADMINCODE in ({})  and Minute = {} and "
               "PRE_1H < 999 and ( Q_PRE_1H is null OR Q_PRE_1H != 2) ) t2 where "
               "t1.stationnum=t2.stationnum".format(end_time, code, minutes)
    }
    try:
        res = requests.post(url, headers=headers, data=data)
    except:
        return '业务内网无法响应！'
    res_js = res.json()
    for d in res_js:
        key = str(d['STATIONNAME'] + d['STATIONNUM'])
        stDatas[key] = d['SUMPRE']
    return stDatas

def replyMinuteRain(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None

    country, is_replay = yield ('TextMsg', '当前为分钟累计雨量查询模式，需要退出雨量查询模式时请输入：9\n\n'
                                           '请输入要查询的县/区：')
    while True:
        try:
            code = get_code(country)
        except:
            country, is_replay = yield ('TextMsg', '未查询到{},请重新输入查询县/区:'.format(country))
            continue
        else:
            if code == '9':
                return ('TextMsg', '退出分钟雨量查询模式，'
                                   '开始新的会话模式请输入对应的数字进入！')
            endTime, minutes = get_time()
            year = endTime[0: 4]
            month = endTime[5: 7]
            day = endTime[8: 10]
            hour = endTime[11: 13]

            msgDatas = ['{}--区域站{}/{}/{} {}时\n  至当前累计 {} 分钟雨量值:'.format(country, year, month,
                                                                          day, hour, minutes)]

            R_datas = down_r(code, endTime, minutes)
            if R_datas == '业务内网无法响应！':
                return 'TextMsg', R_datas + '请稍后重新查询！'
            if not len(R_datas.keys()):
                country, is_replay = yield ('TextMsg', '内网未查询到{}的分钟累计雨量，地名请精确至县/区！\n\n'
                                                       '请重新输入查询县/区：'.format(country))
            else:
                end_R_datas = sorted(R_datas.items(), key=lambda d: d[1], reverse=True)
                for value in end_R_datas:
                    buffData = value[0].ljust(10) + ":\n" + ' ' * 20 + str(value[1]).rjust(10)
                    msgDatas.append(buffData)
                msg = '\n'.join(msgDatas)
                country, is_replay = yield ('TextMsg', msg + '\n\n退出分钟雨量查询请输入：9\n'
                                                             '继续查询请输入要查询的县/区：')
