import json
import time

import requests

from configs import proxies, headers
from amiyabot import log

class ChatGPT:
    url = 'https://api.openai.com/v1/chat/completions'

    def __init__(self, temperature=0.7, system_order=''):
        # 准确度，0到1之间，越小准确度越高，回答也就更精确，但限制更多
        self.temperature = temperature
        self.system_order = system_order

        # 对话组，将所有对话保存在里面
        self.conversations_group = []
        self.add_conversation('system', self.system_order)

        # 对话总token数
        self.tokens_count = 0
        self.next_alarm_token_counts = 30000

        # 会话开始时间
        self.start_time = time.time()

    def get_start_time(self):
        return self.start_time

    def get_conversations_group(self):
        return self.conversations_group

    def get_conversations_count(self):
        """
        获取对话总次数
        :return:
        """
        return len(self.conversations_group)

    def get_tokens_count(self):
        return self.tokens_count

    def get_data(self):
        messages = [conversation['message'] for conversation in self.get_conversations_group()]
        return {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": self.temperature
        }

    def add_conversation(self, role, content):
        """
        添加对话到对话组
        :param role:
        :param content:
        :return:
        """
        self.conversations_group.append(self.gen_conversation(role, content))

    @staticmethod
    def gen_conversation(role, content):
        """
        通过角色和内容生成对话
        :param role:
        :param content:
        :return:
        """
        return {
            "message": {
                "role": role,
                "content": content,
            },
            # 下面是自己加的，不是ChatGPT要求的
            "send_time": time.time()
        }

    def tokens_usage_check(self):
        """
        检查token数，并在有需要时返回值进行报警
        :return:
        """
        if self.get_tokens_count() > self.next_alarm_token_counts:
            self.next_alarm_token_counts += 10000
            return self.get_tokens_count()
        return False

    def call(self, content):
        """
        将新的对话添加到对话组，并请求
        :param content:
        :return:
        """
        self.add_conversation('user', content)
        try:
            ret = requests.post(
                url=ChatGPT.url,
                headers=headers,
                data=json.dumps(self.get_data()),
                proxies=proxies
            ).text
            # print(ret)
            ret_json = json.loads(ret)
        except Exception as e:
            log.error(f"在处理ChatGPT对话时发生了错误: {e}")
            self.conversations_group.pop()
            return f"在处理ChatGPT对话时发生了错误: {e}"
        try:
            answer = ret_json['choices'][0]['message']['content']
            self.tokens_count += int(ret_json['usage']['total_tokens'])
        except Exception as e:
            log.error(f"在处理json时出现错误，{e}，JSON原文为：{str(ret_json)}")
            self.add_conversation('assistant', 'no reply')
            return f"[ChatGPT Handler]在处理json时出现错误，{e}，JSON原文为：{str(ret_json)}"
        self.add_conversation('assistant', answer)
        return answer


    def restart(self):
        """
        重新开始对话，但保留tokens_count计数
        :return:
        """
        self.conversations_group = []
        self.add_conversation('system', self.system_order)

# 用一个字典来保存每个群的ChatGPT对象
gpt_sessions = dict()
