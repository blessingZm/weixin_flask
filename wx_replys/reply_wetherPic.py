# -*- coding: utf-8 -*-
# 根据“天气图+年月日时”从湖北业务内网查询高空天气图！
import requests
from datetime import datetime, timedelta
from wechatpy.replies import ArticlesReply, TextReply


class replyWetherPic:
    # 默认图片类型位高度场
    def __init__(self, receivemsg):
        self.baseurl = 'http://10.104.235.5'
        self.basePicUrl = 'http://10.104.235.4'
        self.receivemsg = receivemsg
        # 位势高度
        self.high = [850, 700, 500, 200]
        self.picType = {'高度场': 'height', '风场': 'uv'}

    def getPic(self):
        dateTime = self.receivemsg.content.replace('天气图', '')
        try:
            pic_time = dateTime.split()[0]
        except:
            return "请输入天气图+查询时间"
        year = pic_time[0: 4]
        month = pic_time[4: 6]
        day = pic_time[6: 8]
        hour = pic_time[8: 10]
        hours = ['08', '20']
        # print hour
        if len(pic_time) is not 10:
            return "请输入正确的查询时间，即年月日时"
        if hour not in hours:
            return "请注意：天气图数据间隔为12小时，即小时只能是08或20"

        nowTime = datetime.strftime(datetime.today() - timedelta(hours=2), '%Y%m%d%H')
        if pic_time > nowTime:
            return "{}/{}/{} {}时的天气图还未形成，请于10/22时后查询当天08/20时的天气图"\
                .format(year, month, day, hour)

        titles = []
        picUrls = []
        description = '中国气象局MICAPS3.2'

        url = self.baseurl + '/NW/weather/getWeatherPic'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Content-Length": "611",
            "Cookie": "JSESSIONID=01FCE2237C08B6917DF51D79293490F2", "Connection": "keep-alive"
        }
        productTime = datetime.strptime(pic_time, '%Y%m%d%H')
        acticles = []
        for key, value in self.picType.items():
            for picHigh in self.high:
                # print(picHigh)
                postData = {"productType": "high",
                            "productHeight": "{}_{}".format(value, picHigh),
                            'productTime': "{}".format(productTime)
                            }
                titles.append('{}/{}/{} {}时{}百帕{}'.format(pic_time[0: 4], pic_time[4: 6],
                                                          pic_time[6: 8], pic_time[8: 10], picHigh, key))
                try:
                    res = requests.post(url, headers=headers, data=postData)
                    picPath = res.json()['data'][0]['imgPath']
                except:
                    return "业务内网未找到{}/{}/{} {}时的天气图".format(year, month, day, hour)
                else:
                    picUrls.append(self.basePicUrl + picPath)
        for i, title in enumerate(titles):
            acticles.append({'title': title, 'description': description,
                             'url': picUrls[i], 'image': picUrls[i]})
        return acticles

    # 数据转为可回复的xml格式
    def replyMsg(self):
        msg = self.getPic()
        if not isinstance(msg, list):
            reply = TextReply(content='{}'.format(msg), message=self.receivemsg)
        else:
            reply = ArticlesReply(message=self.receivemsg, articles=msg)
        # 转换成 XML
        xml = reply.render()
        return xml
