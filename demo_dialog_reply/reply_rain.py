# -*- coding: utf-8 -*-
"""
根据“县/区名+年月日时 雨量”从湖北业务内网查询1、12、24小时雨量
"""
import requests
import sqlite3
from datetime import datetime, timedelta
import pandas as pd


timeText = ['1', '12', '24']

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

def down_r(code, rawTime):
    insertTime = rawTime + '0000'
    stDatas = {}
    endTime = datetime.strptime(insertTime, '%Y%m%d%H%M%S')
    startTimes = [endTime - timedelta(hours=i) for i in [0, 11, 23]]
    url = 'http://10.104.235.5/hbzd/hbase'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Content-Length": "611",
        "Cookie": "JSESSIONID=01FCE2237C08B6917DF51D79293490F2",
        "Connection": "keep-alive"
    }
    i = 0
    for startTime in startTimes:
        stDatas[timeText[i]] = {}
        data = {
            'sql': "select STATIONNAME,t1.STATIONNUM STATIONNUM,PROVINCE,CITY,COUNTY,LATITUDE,LONGITUDE,"
                   "ALTITUDE,SUMPRE from sta_info_reg t1,( select STATIONNUM,SUM(PRE_1H) SUMPRE from "
                   "SURF_DATA_REG where OBSERVTIMES >= to_date('{0}','yyyy-MM-dd HH:mm:ss') and "
                   "OBSERVTIMES <= to_date('{1}','yyyy-MM-dd HH:mm:ss') and PROVINCE='湖北省' and "
                   "ADMINCODE in ({2})  and minute = 0 and PRE_1H < 999 and "
                   "( Q_PRE_1H is null OR Q_PRE_1H != 2) group by stationnum ) t2 where "
                   "t1.stationnum=t2.stationnum UNION ALL select STATIONNAME,t1.STATIONNUM STATIONNUM,"
                   "PROVINCE,CITY,COUNTY,LATITUDE,LONGITUDE,ALTITUDE,SUMPRE from sta_info_test t1,"
                   "( select STATIONNUM,SUM(PRE_1H) SUMPRE from SURF_DATA where OBSERVTIMES >= "
                   "to_date('{0}','yyyy-MM-dd HH:mm:ss') and "
                   "OBSERVTIMES <= to_date('{1}','yyyy-MM-dd HH:mm:ss') and "
                   "PROVINCE='湖北省' and ADMINCODE in ({2})  and "
                   "minute = 0 and PRE_1H < 999 and ( Q_PRE_1H is null OR Q_PRE_1H != 2) "
                   "group by stationnum ) t2 where t1.stationnum=t2.stationnum".format(startTime,
                                                                                       endTime, code),
            'ts': "PRE_1H:"
        }
        try:
            res = requests.post(url, headers=headers, data=data)
        except:
            return '业务内网无法响应！'
        res_js = res.json()
        for d in res_js:
            key = d['STATIONNAME'] + d['STATIONNUM']
            stDatas[timeText[i]][key] = d['SUMPRE']
        i += 1
    return stDatas

def replyRain(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None

    country, is_replay = yield ('TextMsg', '当前为雨量查询模式\n'
                                           '请输入要查询的县/区：')
    while True:
        try:
            code = get_code(country)
        except:
            country, is_replay = yield ('TextMsg', '未查询到{},请重新输入查询县/区:'.format(country))
            continue
        else:
            if code == '9':
                return ('TextMsg', '退出雨量查询模式，'
                                   '开始新的会话模式请输入对应的数字进入！')
            rawTime, is_replay = yield ('TextMsg', '查询地区为：{}，'
                                                   '请输入要查询的时间：'.format(country))
            while True:
                if rawTime == '9':
                    return ('TextMsg', '退出当前会话，'
                                       '开始新的会话模式请输入对应的数字进入！')
                year = rawTime[0: 4]
                month = rawTime[4: 6]
                day = rawTime[6: 8]
                hour = rawTime[8: 10]
                nowTime = datetime.strftime(datetime.today(), '%Y%m%d%H')
                if len(rawTime) < 10:
                    rawTime, is_replay = yield ('TextMsg', "请输入正确的时间格式：年月日时\n"
                                                           "请重新输入查询时间：")
                    continue
                elif rawTime > nowTime or rawTime < '2016123108':
                    rawTime, is_replay = yield ('TextMsg', "请检查查询时间{}/{}/{} {}时"
                                                           "（未到或早于2016/12/31）\n"
                                                           "请重新输入查询时间：".format(year, month, day, hour))
                    continue

                else:
                    break
            maxNum = 30
            msgDatas = ['{}--区域站{}/{}/{} {}时累计1h、12h、24h雨量:'.format(country, year, month, day, hour)]

            R_datas = down_r(code, rawTime)
            if R_datas == '业务内网无法响应！':
                return 'TextMsg', R_datas + '请稍后重新查询！'
            pd_R_datas = pd.DataFrame(R_datas).sort_values(['{}'.format(timeText[-1])], ascending=False)
            if len(pd_R_datas.index) <= maxNum:
                rawDatas = pd_R_datas
            else:
                rawDatas = pd_R_datas.iloc[1: maxNum + 1]
            if not len(rawDatas):
                country, is_replay = yield ('TextMsg', '内网未查询到{}的区域站雨量，地名请精确至县/区\n'
                                                       '请重新输入查询县/区：'.format(country))
            else:
                for i in range(len(rawDatas)):
                    buffData = rawDatas.iloc[i]
                    buffDataR = ','.join([str(r).rjust(10) for r in buffData.values])
                    msgDatas.append(str(buffData.name) + ":")
                    msgDatas.append(' ' * 8 + buffDataR)
                msg = '\n'.join(msgDatas)
                country, is_replay = yield ('TextMsg', msg + '\n\n退出雨量查询请输入：9\n'
                                                          '继续查询请输入要查询的县/区：')
