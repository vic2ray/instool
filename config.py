
"""读取账号文本文件"""
# 格式要求: 一行一个
# 1. sesssionid字符串
# 2. 包含"sessionid=xxx"的字符串
session_file = 'sessionid.txt'

"""登录失败输出"""
fail_output = 'fail_sessionid.txt'

"""代理"""
proxy = 'http://127.0.0.1:7890'

"""每个账号最大采集粉丝数量(达量切号)"""
session_followers_amount = 1000

"""粉丝采集断点保存文件"""
cursor_output = 'cursor.txt'