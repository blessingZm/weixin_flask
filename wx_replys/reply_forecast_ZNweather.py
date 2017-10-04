"""
根据“天气+地区”从中国天气回复天气查询图文消息
"""
from wechatpy.replies import ArticlesReply, TextReply
import requests


class replyForecastChina:
    def __init__(self, receivemsg):
        self.receivemsg = receivemsg
        self.city = receivemsg.content.replace('天气', '')

    # 获取城市对应的id
    def get_code(self):
        try:
            city = self.city.split()[0]
        except:
            return "请输入天气+查询时间"
        code = {}
        url = 'https://api.heweather.com/v5/search'
        data = {
            'city': '{}'.format(city),
            'key': '2053a52f388d44a2871d061597023802'
        }
        res = requests.post(url, data).json()
        cityDatas = res['HeWeather5']
        for i in range(len(cityDatas)):
            cityInfo = cityDatas[i]['basic']
            key = cityInfo['prov'] + '--' + cityInfo['city']
            code[key] = cityInfo['id']
        return code

    def getWeather(self):
        acticles = []
        locCode = self.get_code()
        if not isinstance(locCode, dict):
            return locCode
        city = self.city.split()[0]
        if len(locCode.keys()) < 1:
            return '未查询到{},请重新输入！'.format(city)
        elif len(locCode.keys()) > 1:
            return '查询到多个{0}, 请精确到县/区\n' \
                   '查询到的{0}有：\n{1}'.format(city, ', '.join(list(locCode.keys())))
        else:
            locCode = list(locCode.values())[0].replace('CN', '')
            titles = ['{} 天气预报,详情请查看全文'.format(city)]
            description = '中国天气'
            weatherUrl = ['http://m.weather.com.cn/mweather/{}.shtml'.format(locCode)]
            imgUrl = ['http://i.tq121.com.cn/i/wap2016/news/logo-bottom.png']
            for i, title in enumerate(titles):
                acticles.append({'title': title, 'description': description,
                                 'url': weatherUrl[i], 'image': imgUrl[i]})
            return acticles

    # 数据转为可回复的xml格式
    def replyMsg(self):
        msg = self.getWeather()
        # print(msg)
        if not isinstance(msg, list):
            reply = TextReply(content='{}'.format(msg), message=self.receivemsg)
        else:
            reply = ArticlesReply(message=self.receivemsg, articles=msg)
        # 转换成 XML
        xml = reply.render()
        return xml
