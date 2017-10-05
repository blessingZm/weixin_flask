# -*- coding: utf-8 -*-
# 回复人物图片消息，自动识别性别和年龄
import requests
import re


def replyImginfo(picurl):
    s = requests.session()
    url = 'https://how-old.net/Home/Analyze?isTest=False&source=&version=how-old.net'
    header = {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Host': "how-old.net",
        'Referer': "http://how-old.net/",
        'X-Requested-With': "XMLHttpRequest"
    }

    data = {'file': s.get(picurl).content}
    try:
        r = s.post(url, files=data, headers=header)
        h = str(r.content)
        i = h.replace('\\', '')
        gender = re.search(r'"gender": "(.*?)"rn', i)
        age = re.search(r'"age": (.*?),rn', i)
        if gender.group(1) == 'Male':
            gender1 = '男'
        else:
            gender1 = '女'
        datas = [gender1, age.group(1)]
        msg = '图中人物性别为:' + datas[0] + '\n' + '年龄为:' + datas[1]
    except:
        msg = '识别失败，换张图片试试吧'
    return msg
