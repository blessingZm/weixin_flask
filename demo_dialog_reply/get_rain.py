# -*- coding: utf-8 -*-
"""根据地区及时间从湖北业务内网下载1h、6h、12h、24h雨量"""
import requests
import re
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from collections import OrderedDict

timeText = ['1', '6', '12', '24']
re_str = re.compile('^([\u4e00-\u9fa5]+)\s*(\d+)\s*雨量$')


def read_code(country):
    dbName = 'coding.db'
    tableName = 'coding'
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    db_command = "select id from {} where address like '%{}%'".format(tableName, country)
    cursor.execute(db_command)
    code = cursor.fetchone()[0]
    return code


def down_r(insertTime, country):
    stDatas = OrderedDict()
    endTime = datetime.strptime(insertTime, '%Y%m%d%H%M%S')
    startTimes = [endTime - timedelta(hours=i) for i in [0, 5, 11, 23]]
    try:
        adminCode = read_code(country)
    except:
        return '未查询到地名：{}'.format(country)

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
                                                                                       endTime, adminCode),
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

def get_rain(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None

    locAndTime = re_str.findall(receiveData)[0]
    country = locAndTime[0]
    rawDateTime = locAndTime[1]
    insertTime = rawDateTime + '0000'
    year = rawDateTime[0: 4]
    month = rawDateTime[4: 6]
    day = rawDateTime[6: 8]
    hour = rawDateTime[8: 10]
    if len(rawDateTime) is not 10:
        msg_content = "请输入正确的查询时间，即年月日时"
        return ('TextMsg', msg_content)

    nowTime = datetime.strftime(datetime.today(), '%Y%m%d%H')
    if rawDateTime > nowTime or rawDateTime < '2016123108':
        msg_content = "请检查查询时间{}/{}/{} {}时" \
                      "（未到或早于2016/12/31）！".format(year, month, day, hour)
        return ('TextMsg', msg_content)

    maxNum = 30
    msgDatas = [
        '{}--区域站{}/{}/{} {}时累计1h、6h、12h、24h雨量:'.format(country, year, month, day, hour)]
    R_datas = down_r(insertTime, country)

    if R_datas == '未查询到地名：{}'.format(country) or \
        R_datas == '业务内网无法响应！':
        msg_content = R_datas
        return ('TextMsg', msg_content)

    pd_R_datas = pd.DataFrame(R_datas).sort_values(['{}'.format(timeText[-1])], ascending=False)
    if len(pd_R_datas.index) <= maxNum:
        rawDatas = pd_R_datas
    else:
        rawDatas = pd_R_datas.iloc[1: maxNum + 1]
    if not len(rawDatas):
        msg_content = '内网未查询到{}的区域站雨量，地名请精确至县/区！'.format(country)
    else:
        for i in range(len(rawDatas)):
            buffData = rawDatas.iloc[i]
            buffDataR = ','.join([str(r).rjust(8) for r in buffData.values])
            msgDatas.append(str(buffData.name) + ":")
            msgDatas.append(' '*4 + buffDataR)
        msg_content = '\n'.join(msgDatas)
    return ('TextMsg', msg_content)
