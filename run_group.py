import sys
import random

from datetime import datetime
from playwright import sync_api

from insapi import InsApi
from utils import get_username, get_cookies, logger, extra_message, get_message, get_proxy
from config import group_dm_delay, group_limits, group_round, headless, group_num

# 用户名文件
user_file = sys.argv[1] if len(sys.argv) > 1 else 'lalalalisa_m.txt'  # 'lalalalisa_m.txt'
# 发送消息文本
message_file = sys.argv[2] if len(sys.argv) > 2 else 'message.txt'

users = get_username(user_file)
message_text = extra_message( get_message(message_file) )

def run_group(cl):

    def fill_user(username):
        print('正在添加用户', username)
        search_input = page.get_by_placeholder('搜索…')
        search_input.fill(username)
        try:
            if check_box := page.wait_for_selector('xpath=//input[@name="ContactSearchResultCheckbox"]', timeout=3000):
                if not check_box.is_checked():
                    check_box.click()
                    page.wait_for_timeout(5000)
                    return True
        except Exception as e:
            search_input.fill('')
            return False
        
    proxy = cl.proxy
        
    with sync_api.sync_playwright() as pw:
        UserAgents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",  # noqa: E501
        ]
        args = ['--no-sandbox', '--disable-web-security', '--disable-features=site-per-process',
            '--disable-plugins', '--disable-extentions', '--disable-dev-shm-usage', '--ignore-certificate-errors',
            '--disable-gpu', '--disable-blink-features=AutomationControlled', f'--proxy-server={proxy}']
        browser_fingers = {
            "color_scheme": "dark",
            "geolocation": { "latitude": 85, "longitude": -25, "accuracy": 0 },
            "has_touch": False, "is_mobile": False, "locale": "zh-CN", "timezone_id": "Asia/Shanghai",
            "viewport": { "width": 1440, "height": 768 },
            "user_agent": random.choice(UserAgents)
        }
        browser = pw.chromium.launch(headless=headless, args=args)
        context = browser.new_context(**browser_fingers)
        context.add_cookies(cookies=get_cookies(cl.sessionid))
        page = context.new_page()

        page.goto('https://www.instagram.com/direct/inbox/', timeout=60000)
        # 等待页面加载完成
        page.wait_for_load_state('load', timeout=60000)

        # 去除打开消息通知遮罩层
        try:
            button_text = '打开'
            xpath_expression = f"//button[text()='{button_text}']"
            button = page.wait_for_selector(f"xpath={xpath_expression}", strict=True, timeout=10000)
            if button: button.click()  # 按钮存在，执行点击操作
        except Exception as e:
            pass

        # 查找最后建的群组, 确定最后发送消息时间
        # threads = cl.direct_threads()
        # group = None
        # last_active_at = None
        # meet_dm_delay = False  # 是否达到时间间隔要求
        # for thread in threads:
        #     if thread.is_group and thread.admin_user_ids[0] == cl.user_id:
        #         group = thread
        #         break
        # 存在群组, 查找最近群组的最近20条群组消息, 获取管理员发布消息的最后时间
        # if group:
        #     print(group.id, len(group.users), group.thread_title)
        #     messages = cl.direct_messages(group.id)
        #     # 如果没有主动发送消息的最后时间, 则取最后一条群组消息的时间
        #     last_active_at = messages[0].timestamp
        #     for message in messages:
        #         if int(message.user_id) == cl.user_id:
        #             if message.item_type == 'media':
        #                 print('[图片消息]', message.timestamp.isoformat(), message.media.thumbnail_url)
        #                 last_active_at = message.timestamp
        #                 break
        #             if message.item_type == 'xma_link':
        #                 print('[文字消息]', message.timestamp.isoformat(), message.text)
        #                 last_active_at = message.timestamp
        #                 break
        #     print('最后管理员消息或群组活跃时间', last_active_at.isoformat())
        #     timedelta = (datetime.now() - group.messages[0].timestamp).total_seconds() // 60
        #     if timedelta >= group_dm_delay:
        #         print('满足设定群组创建和消息间隔, 即将创建新的群组')
        #         meet_dm_delay = True
        # 如果最后消息发送时间满足设定间隔(15分钟以上或更久), 则可以创建群组和发送消息
        # if group and not meet_dm_delay:
        #     print('不满足设定群组创建和消息间隔, 请等待一段时间后重试')
        #     return False
        # else:
        for i in range(group_num):
            # 读取用户进行拉群
            # page.goto('https://www.instagram.com/direct/t/7188984047860738')
            button_text = '新消息'
            if button := page.locator(selector='div > svg', has_text=button_text):
                # 先拉5个人建群
                try:
                    if button.is_visible() and button.is_enabled():
                        button.click(timeout=10000)
                        for i in range(group_round): fill_user(next(users))
                        page.get_by_text('聊天').click(timeout=30000)
                        page.wait_for_load_state('networkidle')
                    else:
                        print('无头模式下新建按钮不可点击')
                        return False
                except Exception as e:
                    logger.exception(e)
                    print('群组创建失败!', e)
                    return False
                print('正在创建群组...')
                # 拉人
                try:
                    page.locator(selector='div > svg', has_text="对话信息").click(timeout=30000)
                    page.wait_for_timeout(5000)
                except Exception as e:
                    print('群组创建失败!', e)
                    return False
                page.get_by_text("添加用户").click(timeout=5000)
                page.wait_for_timeout(1000)
                for i in range(group_limits // group_round + 1):
                    for i in range(group_round): fill_user(next(users))
                    page.get_by_text('继续').click(timeout=5000)
                    page.wait_for_timeout(1000)
                    if i != group_limits // group_round:
                        page.get_by_text("添加用户").click(timeout=5000)
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
                    return False

        page.wait_for_timeout(10000)
        page.close()
        context.close()
        browser.close()


insapi = InsApi()
while True:
    insapi.get_login()
    if insapi.all_session_fail:
        break
    if insapi.has_login:
        # 拉群
        try:
            if run_group(insapi.cl):
                continue
            else:
                insapi.faillogin_set.add(insapi.cl.sessionid)
        except Exception as e:
            print('发生异常', e)
            insapi.faillogin_set.add(insapi.cl.sessionid)
    # 所有账号异常
    else:
        break