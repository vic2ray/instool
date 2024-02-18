from playwright import sync_api
from instagrapi import Client
import sys

sessionid = ''
with open('sessionid.txt', 'r', encoding='utf-8') as f:
    sessionid = f.read().strip()
    print('读取sessionid', sessionid)

cl = Client()
cl.set_proxy('http://127.0.0.1:7890')
cl.login_by_sessionid(sessionid)

print(cl.sessionid)

def get_user_followers(user_id, amount):
    max_id = ''
    return_hits = 0
    while return_hits < amount:
        users, max_id = cl.user_followers_v1_chunk(user_id, max_amount=200, max_id=max_id)
        # users, max_id = cl.user_followers_gql_chunk(user_id, max_amount=200, end_cursor=max_id)
        yield from users
        return_hits += len(users)
        if not max_id: 
            break

cookies = [
    {
        "domain": ".instagram.com",
        "expirationDate": 1739416483.655826,
        "hostOnly": False,
        "httpOnly": True,
        "name": "sessionid",
        "path": "/",
        "secure": True,
        "session": False,
        "storeId": "0",
        "value": cl.sessionid,
        "id": 12
    },
]

with sync_api.sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies=cookies)
    page = context.new_page()
    page.goto('https://www.instagram.com/')
    page.wait_for_timeout(1000)
    
    user_id = sys.argv[1] if len(sys.argv) > 2 else '63682075709'  # trump
    amount = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    print('爬取中...')
    for idx, user in enumerate(get_user_followers(user_id, amount)):
        print(idx, user.pk)
        userstr = f'{user.pk} {user.username} {user.full_name}\n'
        with open(f'{user_id}_{amount}.txt', 'a', encoding='utf-8') as fp:
            fp.write(userstr)
    print('爬取完成')
    page.wait_for_timeout(10000)
    page.close()
    context.close()
    browser.close()
