"""
关注时的处理！

"""

def replyWelcome(to_user, receiveData):
    yield None
    msg_content, is_replay = yield None
    msg = "欢迎关注我的个人微信订阅号! \n\n" \
          "回复以下数字进入相应的对话模式:\n" \
          "【0】 查看详细功能参数；\n" \
          "【1】 未来5天天气预报查询；\n" \
          "【2】 区域站雨量信息查询，仅支持湖北地区\n" \
          "【3】 与机器人（ZM助手）聊天模式；\n" \
          "【9】 处于某会话模式时，用于退出当前模式；\n\n"
    return ('TextMsg', msg)
