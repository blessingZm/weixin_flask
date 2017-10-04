# -*- coding: utf-8 -*-
"""
从湖北业务内网，根据“数值预报+年月日时 位势高度”查询欧洲数值预报图
"""
import requests
from datetime import datetime, timedelta
from wechatpy.replies import ArticlesReply, TextReply


class replyForecastPic:
    def __init__(self, receivemsg):
        self.baseurl = 'http://10.104.235.5'
        self.basePicUrl = 'http://10.104.235.4'
        self.receivemsg = receivemsg
        self.highs = ['500', '700', '850', '200']

    def getPic(self):
        content = self.receivemsg.content.replace('数值预报', '')
        try:
            dateTime = content.split()[0]
            height = content.split()[1]
        except:
            return '请输入正确的查询格式，数值预报+年月日时+空格+位势高度,' \
                  '注意时间与位势高度之间有一个空格，如：数值预报2017093020 500'
        pic_time = dateTime
        year = pic_time[0: 4]
        month = pic_time[4: 6]
        day = pic_time[6: 8]
        hour = pic_time[8: 10]
        hours = ['08', '20']
        if len(pic_time) is not 10:
            return "请输入正确的查询时间，即年月日时"
        if hour not in hours:
            return "请注意：天气图数据间隔为12小时，即小时只能是08或20"

        nowTime = datetime.strftime(datetime.today() - timedelta(days=1), '%Y%m%d%H')
        if pic_time[0: 8] > nowTime[0: 8]:
            return "{}/{}/{} {}时的预报图还未形成，请保证查询的日期至少为当前时间前一天"\
                .format(year, month, day, hour)
        if height not in self.highs:
            return '请输入正确的位势高度，只能为200或500或700或850'

        if height == '500':
            picType = {'高度场': 'height', '风场': 'uv'}
            prescripTime = [24, 48, 72, 96]
        else:
            picType = {'风场': 'uv'}
            prescripTime = [24, 48, 72, 96, 120]

        titles = []
        picUrls = []
        description = '中国气象局MICAPS3.2'

        url = self.baseurl + '/NW/numforecast/getNumForecastPic'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Content-Length": "611",
            "Cookie": "JSESSIONID=01FCE2237C08B6917DF51D79293490F2", "Connection": "keep-alive"
        }
        productTime = datetime.strptime(pic_time, '%Y%m%d%H')

        for key, value in picType.items():
            postData = {"productType": "ecmwf",
                        "productHeight": "{}_{}".format(value, height),
                        'productTime': "{}".format(productTime)}
            for n, preTime in enumerate(prescripTime):
                forecast_time = datetime.strptime(dateTime, '%Y%m%d%H') + timedelta(hours=preTime)
                forecast_time = datetime.strftime(forecast_time, '%Y%m%d%H')
                titles.append('{}  {}/{}/{} {}时ECMWF{}百帕{}日{}时预报'.format(key, pic_time[0: 4], pic_time[4: 6],
                                                                         pic_time[6: 8], pic_time[8: 10], height,
                                                                         forecast_time[6: 8], forecast_time[8: 10]))
            try:
                res = requests.post(url, headers=headers, data=postData)
                picPaths = res.json()['data']
            except:
                return "业务内网未找到{}/{}/{} {}时的预报图".format(year, month, day, hour)
            else:
                for i in range(len(prescripTime)):
                    picUrls.append(self.basePicUrl + picPaths[i]['imgPath'])

        acticles = []
        for i, title in enumerate(titles):
            acticles.append({'title': title, 'description': description,
                             'url': picUrls[i], 'image': picUrls[i]})
        return acticles

    # 数据转为可回复的xml格式
    def replyMsg(self):
        msg = self.getPic()
        # print(msg)
        if not isinstance(msg, list):
            reply = TextReply(content='{}'.format(msg), message=self.receivemsg)
        else:
            reply = ArticlesReply(message=self.receivemsg, articles=msg)
        # 转换成 XML
        xml = reply.render()
        return xml
