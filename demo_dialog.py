# -*- coding: utf-8 -*-
# 从 __init__ 导入ROUTER中的所有处理函数
from __init__ import *

# REDIS 配置，请自行替换
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = 'foobared'
REDIS_DB = 0
# REDIS KEY的格式，会接收用户的open_id作为变量
# 如：REDIS_KEY % {'open_id': '11'}， 最终结果即为'wechat-dialog:demo:11'
# 详情查看python字符串格式化 %操作符，用词典传递真实值
REDIS_KEY = 'wechat-dialog:demo:%(open_id)s'

# 初始配置，根据用户信息分配对应的会话处理器
# 格式为(<匹配模式>, <处理函数>), 匹配模式为正则表达式
# 通过is_replay避免重复执行某段代码
# 通过raise UnexpectAnswer将某个不合法输入当做下一个输入的入口
ROUTER = {
    'text': [
        ('^0$', 'replyFunction'),
        ('^1$', 'replyForecast'),
        ('^2$', 'replyRain'),
        ('^3$', 'replyTulin'),
        ('^[\u4e00-\u9fa5]+\s*天气$', 'get_weather'),
        ('^[\u4e00-\u9fa5]+\s*\d+\s*雨量$', 'get_rain'),
        ('.*', 'replyFunction')
    ],
    'event': [
        ('subscribe', 'replyWelcome'),
        ('.*', 'replyFunction')
    ],
    'image': [
        ('.*', 'replyImginfo')
    ],
}
