import sys
from playwright import sync_api
from instagrapi import Client

sessionid = '62883843682%3ACzqCupvclzilRN%3A14%3AAYdYTH23fUE7vD3xTFRic9-zNnQEpF734_ZyzYiFBQ'
user_files = '63682075709_100.txt'
# 设定群组人数
group_limits = 30  
# 群组消息
message_text = 'Does anybody have some good things to share with? Happy Chinese New year! Wish you have a good day! '
# 设定群组消息间隔时间
group_dm_delay = 15
# 开启有头可视化
headless = False

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

def get_users():
    with open(user_files, 'r', encoding='utf-8') as fp:
        for line in fp.readlines():
            username = line.split()[1]
            yield username

def fill_user(username):
    print('正在添加用户', username)
    search_input = page.get_by_placeholder('搜索…')
    search_input.fill(username)
    try:
        if check_box := page.wait_for_selector('xpath=//input[@name="ContactSearchResultCheckbox"]', timeout=3000):
            if not check_box.is_checked():
                check_box.click()
                page.wait_for_timeout(1000)
                return True
    except Exception as e:
        search_input.fill('')
        return False

with sync_api.sync_playwright() as pw:
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context()
    context.add_cookies(cookies=cookies)
    page = context.new_page()
    # page.goto('https://www.instagram.com/')
    # page.wait_for_timeout(1000)
    
    # user_id = '63682075709'  # trump
    # amount = 100
    # for idx, user in enumerate(get_user_followers(user_id, amount)):
    #     print(idx, user.pk)
    #     userstr = f'{user.pk} {user.username} {user.full_name}\n'
    #     with open(f'{user_id}_{amount}.txt', 'a', encoding='utf-8') as fp:
    #         fp.write(userstr)

    page.goto('https://www.instagram.com/direct/inbox/')
    # 等待页面加载完成
    page.wait_for_load_state('load')

    # 去除打开消息通知遮罩层
    button_text = '以后再说'
    xpath_expression = f"//button[text()='{button_text}']"
    button = page.query_selector(f"xpath={xpath_expression}")
    if button: button.click()  # 按钮存在，执行点击操作

    # 获取最新发布消息的时间

    from datetime import datetime


    # 查找最后建的群组, 确定最后发送消息时间
    threads = cl.direct_threads()
    group = None
    last_active_at = None
    meet_dm_delay = False  # 是否达到时间间隔要求
    for thread in threads:
        if thread.is_group and thread.admin_user_ids[0] == cl.user_id:
            group = thread
            break
    # 存在群组, 查找最近群组的最近20条群组消息, 获取管理员发布消息的最后时间
    if group:
        print(group.id, len(group.users), group.thread_title)
        messages = cl.direct_messages(group.id)
        # 如果没有主动发送消息的最后时间, 则取最后一条群组消息的时间
        last_active_at = messages[0].timestamp
        for message in messages:
            if int(message.user_id) == cl.user_id:
                if message.item_type == 'media':
                    print('[图片消息]', message.timestamp.isoformat(), message.media.thumbnail_url)
                    last_active_at = message.timestamp
                    break
                if message.item_type == 'xma_link':
                    print('[文字消息]', message.timestamp.isoformat(), message.text)
                    last_active_at = message.timestamp
                    break
        print('最后管理员消息或群组活跃时间', last_active_at.isoformat())
        timedelta = (datetime.now() - group.messages[0].timestamp).total_seconds() // 60
        if timedelta >= group_dm_delay:
            print('满足设定群组创建和消息间隔, 即将创建新的群组')
            meet_dm_delay = True
    # 如果最后消息发送时间满足设定间隔(15分钟以上或更久), 则可以创建群组和发送消息
    if group and not meet_dm_delay:
        print('不满足设定群组创建和消息间隔, 请等待一段时间后重试')
    else:
        # page.goto('https://www.instagram.com/direct/t/' + group.id)
        # page.wait_for_load_state('networkidle')

        # 读取用户进行拉群
        users = get_users()
        button_text = '新消息'
        if button := page.locator(selector='div > svg', has_text=button_text):
            # 先拉5个人建群
            try:
                button.click(timeout=2000)
                username = next( users )
                fill_user(username)
                username = next( users )
                fill_user(username)
                username = next( users )
                fill_user(username)
                username = next( users )
                fill_user(username)
                username = next( users )
                fill_user(username)
                page.get_by_text('聊天').click(timeout=3000)
                page.wait_for_load_state('networkidle')
                pass
            except Exception as e:
                print('群组创建失败!', e)
                sys.exit()
            # page.goto('https://www.instagram.com/direct/t/7188984047860738')
            print('正在创建群组...')
            # 拉人
            try:
                page.locator(selector='div > svg', has_text="对话信息").click(timeout=30000)
                page.wait_for_timeout(1000)
            except Exception as e:
                print('群组创建失败!', e)
                sys.exit()
            page.get_by_text("添加用户").click(timeout=3000)
            page.wait_for_timeout(1000)
            for i in range(group_limits // 5 + 1):
                fill_user(next( users ))
                fill_user(next( users ))
                fill_user(next( users ))
                fill_user(next( users ))
                fill_user(next( users ))
                page.get_by_text('继续').click(timeout=3000)
                page.wait_for_timeout(1000)
                if i != group_limits // 5:
                    page.get_by_text("添加用户").click(timeout=3000)
                    page.wait_for_timeout(1000)
            page.keyboard.press('Escape')
            # 发消息
            try:
                if message_button := page.locator('xpath=//div[@aria-label="发消息"]/p'):
                    message_button.click()
                    message_button.fill( message_text )
                    page.get_by_role("button", name="发送").click()
                    print('消息发送成功')
            except Exception as e:
                print("消息发送失败", e)
            
        # cl.direct_send('Hello, happy new year! ', user_ids=[cl.user_id, 3106386257])
        # cl.direct_send('Hello', thread_ids=[group.id])  # 发送文本消息
        # cl.direct_send_photo(photo_path, thread_ids=[group.id])  # 发送图片消息
        pass

    page.wait_for_timeout(50000)
    page.close()
    context.close()
    browser.close()
