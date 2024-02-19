import sys

from insapi import InsApi

# 采集博主用户名或ID
username = sys.argv[1] if len(sys.argv) > 1 else '63682075709'  # trump
# 采集粉丝数量
amount = int(sys.argv[2]) if len(sys.argv) > 2 else 200
# 采集断点: 采集中断后在控制台获取, 若置空则自动读取cursor.txt最后一行
cursor = sys.argv[3] if len(sys.argv) > 3 else ''

insapi = InsApi()
insapi.get_login()
if insapi.has_login:
    for idx, user in enumerate(insapi.get_followers(username, amount, cursor)):
        userstr = f'{user.pk} {user.username}'
        print(idx, userstr, end='\r')
        with open(f'{username}.txt', 'a', encoding='utf-8') as fp:
            fp.write(f'{userstr}\n')