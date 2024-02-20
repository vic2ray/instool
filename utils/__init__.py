import pathlib
import re
import random
import time
from loguru import logger


def get_sessionid(path):
    """获取sessionid
    读取指定文本内容, 一行一个, 包含sessionid
    返回迭代器, 按需获取
    """
    with open(path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f.readlines(), start=1):
            line = line.strip()
            print(f'读取第 {idx} 行账号: {line}')
            pattern = re.compile(r'(?<=sessionid=).*?(?=\|)')
            if result := re.search(pattern, line):
                sessionid = result.group(0)
            else:
                sessionid = line
            yield sessionid

def get_lines(path):
    """获取文本行数
    在不加载整个文件到内存中的情况下计算行数
    """
    with open(path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
        return line_count

def get_lastline(path):
    """获取文本最后一行
    """
    if not pathlib.Path(path).exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        last_line = None
        for line in f:
            if line and "====================" not in line:
                last_line = line
        if last_line is not None:
            return last_line.strip()
    
def txt_logger(path, message):
    """文本记录器
    向指定文件输出日志信息
    """
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'{message}\n')

def get_cookies(sessionid):
    """浏览器设置Cookie"""
    return [
        {
            "domain": ".instagram.com",
            "expirationDate": None,
            "hostOnly": False,
            "httpOnly": True,
            "name": "sessionid",
            "path": "/",
            "secure": True,
            "session": False,
            "storeId": "0",
            "value": sessionid,
            "id": 12
        },
    ]


def get_username(path):
    """获取用户名
    读取指定文本内容, 一行一个 "pk 用户名"
    返回迭代器, 按需获取"""
    with open(path, 'r', encoding='utf-8') as fp:
        for line in fp.readlines():
            username = line.split()[1]
            yield username

def get_message(path):
    """获取消息文本
    读取指定文本内容
    """
    with open(path, 'r', encoding='utf-8') as fp:
        return fp.read().strip()

def extra_message(text, num_strings=3):
    """向文本中随机位置加入三段时间字符串"""
    modified_text = text

    for _ in range(num_strings):
        random_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 在文本中插入时间字符串
        position = random.randint(0, len(modified_text))
        modified_text = modified_text[:position] + " " + random_string + " " + modified_text[position:]

    return modified_text