
"""读取账号文本文件"""
# 格式要求: 一行一个
# 1. sesssionid字符串
# 2. 包含"sessionid=xxx"的字符串
session_file = 'sessionid.txt'

"""登录失败输出"""
fail_output = 'fail_sessionid.txt'

"""固定代理"""
proxy = ''

"""动态代理"""
proxy_url = "http://api.proxy.ipidea.io/getBalanceProxyIp?num=100&return_type=json&lb=1&sb=0&flow=1&regions=&protocol=http"

"""每个账号最大采集粉丝数量(达量切号)"""
session_followers_amount = 1000

"""粉丝采集断点保存文件"""
cursor_output = 'cursor.txt'

"""设定新建群组间隔时间"""
group_dm_delay = 0

"""设定群组人数"""
group_limits = 10

"""设定单号每次拉群数量"""
group_num = 3

"""设定每次拉人数量"""
group_round = 10

"""设定单号每次分享次数"""
share_num = 5

"""设定每次分享数量"""
share_round = 10

"""关闭有头可视化"""
headless = False  # 开启无头模式下元素不可点击, 不能模拟点击