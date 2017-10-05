"""
关注/取消关注时的处理！

"""

def replyEvent(receivexml, Event):
    if Event == 'subscribe':
        msg = "欢迎关注我的个人微信订阅号! \n\n" \
              "本订阅号支持:\n" \
              "（1）回复“功能”，查看详细功能参数说明；\n" \
              "（2）回复“地名+天气”查询未来5天天气预报；\n" \
              "（3）回复“县/区名 年月日时+雨量”查询区域站雨量信息\n" \
              "（4）回复“天气图+年月日时”，获取高空天气图；\n" \
              "（5）回复“数值预报+年月日时 位势高度”获取欧洲数值预报图；\n" \
              "（6）回复其他信息或语音，与机器人（ZM助手）聊天；\n" \
              "（7）回复人物图片，智能识别人物性别与年龄（仅供娱乐）"\
              "功能持续开发中...."
    elif Event == 'unsubscribe':
        msg = "欢迎随时回来！"
    elif Event == 'location':
        msg = "你的地理位置：\n" \
              "经度：{} \n" \
              "纬度：{}".format(receivexml.longitude, receivexml.latitude)
    return msg
