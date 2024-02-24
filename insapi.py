from instagrapi import Client

from utils import txt_logger, get_sessionid, logger, get_lines, get_lastline, get_proxy
from config import session_file, fail_output, session_followers_amount, cursor_output


class InsApi:
    def __init__(self) -> None:
        self.cl = Client()

        # 账号读取
        self.sessionid_generator = get_sessionid(session_file)
        self.sessionid_count = get_lines(session_file)  # 账号总量

        # 账号登录状态
        self.has_login = False  # 当前是否存在已登录账号
        self.faillogin_count = 0   # 登录失败计数器, 全部失败停止读取
        self.all_session_fail = False  # 所有账号失败停止执行请求
        self.faillogin_set = set()  # 登录失败账号缓存集

    def login(self, sessionid: str):
        """登录
        仅使用sessiondid登录
        """
        try:
            self.cl.proxy = get_proxy()
            self.cl.login_by_sessionid(sessionid)
            logger.info(f'{self.cl.user_id} 登录成功')
            self.has_login = True
            return True
        except Exception as e:
            logger.warning(f'登录失败 {sessionid}, {e}')
            self.faillogin_set.add(sessionid)
            if sessionid in self.faillogin_set:
                txt_logger(fail_output, sessionid)
            self.has_login = False
            return False
        
    def get_login(self):
        """登录调度
        当前账号登录失败或API执行失败时, 继续读取下一账号登录
        当读取到末尾, 从头开始读取第二轮
        当读取账号登录失败过, 直接跳过
        """
        try:
            sessionid = next(self.sessionid_generator)
            if sessionid not in self.faillogin_set:
                self.login(sessionid)
                if not self.has_login: 
                    self.faillogin_count += 1
                    self.get_login()
            # 失败缓存中的账号不执行二次登录
            else:
                self.faillogin_count += 1
                self.get_login()
        except StopIteration:
            if self.faillogin_count >= self.sessionid_count:
                logger.error('全部账号发生异常')
                self.all_session_fail = True
            else:
                logger.warning('已读取完一轮账号, 重新开始读取')
                # 重置读行迭代器
                self.sessionid_generator = get_sessionid(session_file)
                self.faillogin_count = 0
                self.get_login()

    def get_userid(self, username):
        """转换用户名为用户ID"""
        if not username.isdigit():
            try:
                user_id = self.cl.user_id_from_username(username)
                return user_id
            except Exception as e:
                logger.warning(f'转换用户名ID异常: {username} {e}')
        else:
            return username
    
    def get_followers(self, username, amount, cursor: str = ''):
        """用户粉丝采集
        采集策略: 
            1. 每个号采集固定数量粉丝后切换账号
            2. 采集中途发生异常后切换账号
            3. 所有账号采集完一轮未达到数量, 开启第二轮采集
        """
        count = 0
        session_count = 0
        task_str = f'{"="*20} {username} {amount} {"="*20}'
        if not cursor:
            if line := get_lastline(cursor_output):
                _, cursor = line.split()
                print(f'读取采集断点: {cursor}')
        logger.info(f'执行采集任务: {task_str}')
        txt_logger(cursor_output, task_str)
        while count < amount:
            # 所有账号无效控制
            if self.all_session_fail: break
            # 单次采集控制
            try:
                users, cursor = self.cl.user_followers_v1_chunk(
                    self.get_userid(username), 
                    max_amount=200, 
                    max_id=cursor
                )
            except Exception as e:
                logger.warning(f'粉丝采集发生异常: {e}, 当前采集断点: {cursor}, 切换账号继续采集')
                self.faillogin_set.add(self.cl.sessionid)  # 发生异常(频率限制)视为失败登录, 本次运行不再继续采集
                self.get_login()
                if self.has_login: 
                    continue
                else:
                    break
            # users, max_id = cl.user_followers_gql_chunk(user_id, max_amount=200, end_cursor=max_id)
            # 采集结果输出
            yield from users
            count += len(users)
            session_count += len(users)
            logger.info(f'当前账号采集数量: {session_count}, 采集总量: {count}, 采集断点: {cursor}')
            txt_logger(cursor_output, f'{count} {cursor}')
            # 采集结束控制
            if not cursor: 
                logger.warning(f'用户无更多粉丝, 可能是由于隐私设置仅展示一页')
                break
            # 单号采集数量控制
            if session_count >= session_followers_amount:
                logger.warning(f'单次会话账号采集数量已达到采集要求: {session_count} > {session_followers_amount}, 切换账号继续采集')
                session_count = 0  # 重置单个会话采集数量
                self.get_login()
                if self.has_login: 
                    continue
                else:
                    break
        logger.warning(f'采集完成: {count}, 采集断点: {cursor}, 接续采集请复制最后一个断点cursor值')
