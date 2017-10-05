# -*- coding: utf-8 -*-
"""
根据“县/区名+年月日时 雨量”从湖北业务内网查询1、12、24小时雨量
"""
import requests
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import re


# 文字匹配规则
re_text =re.compile(u"[\u4e00-\u9fa5]+")
re_datetime = re.compile('\d{10}')
timeText = ['1', '12', '24']

class replyRain:
    def __init__(self, content):
        self.content = content

    # 从传来的消息中分离地区和时间
    def get_country_rawtime(self):
        Content = self.content.replace('雨量', '')
        country = re.findall(re_text, Content)[0]
        rawTime = re.findall(re_datetime, Content)[0]
        return country, rawTime

    def read_code(self):
        country, rawTime = self.get_country_rawtime()
        dbName = 'coding.db'
        tableName = 'coding'
        db = sqlite3.connect(dbName)
        cursor = db.cursor()
        db_command = "select id from {} where address like '%{}%'".format(tableName, country)
        cursor.execute(db_command)
        code = cursor.fetchone()[0]
        return code

    def down_r(self):
        country, rawTime = self.get_country_rawtime()
        insertTime = rawTime + '0000'
        stDatas = {}
        endTime = datetime.strptime(insertTime, '%Y%m%d%H%M%S')
        startTimes = [endTime - timedelta(hours=i) for i in [0, 11, 23]]
        try:
            adminCode = self.read_code()
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

    def getRain(self):
        try:
            country, rawTime = self.get_country_rawtime()
        except:
            return "请输入地名+年月日时+雨量，注意时间格式！"
        year = rawTime[0: 4]
        month = rawTime[4: 6]
        day = rawTime[6: 8]
        hour = rawTime[8: 10]
        nowTime = datetime.strftime(datetime.today(), '%Y%m%d%H')
        if rawTime > nowTime or rawTime < '2016123108':
            return "请注意查询时间{}/{}/{} {}时（未到或早于2016/12/31）".format(year, month, day, hour)

        maxNum = 30
        msgDatas = [
            '{}--区域站{}/{}/{} {}时累计1h、12h、24h雨量:'.format(country, year, month, day, hour)]

        R_datas = self.down_r()
        if R_datas == '未查询到地名：{}'.format(country) or R_datas == '业务内网无法响应！':
            return R_datas

        pd_R_datas = pd.DataFrame(R_datas).sort_values(['{}'.format(timeText[-1])], ascending=False)
        pd_R_datas.columns.name = '累计时间(h)'
        if len(pd_R_datas.index) <= maxNum:
            rawDatas = pd_R_datas
        else:
            rawDatas = pd_R_datas.iloc[1: maxNum + 1]
        for i in range(len(rawDatas)):
            buffData = rawDatas.iloc[i]
            buffDataR = ','.join([str(r).rjust(10) for r in buffData.values])
            msgDatas.append(str(buffData.name) + ":")
            msgDatas.append(' '*8 + buffDataR)
        return '\n'.join(msgDatas)
