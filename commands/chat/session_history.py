import time
import shlex

from amiyabot import Message, Chain, log

from ai.gpt.chatgpt import gpt_sessions
from configs import bot, normal_order_level, sender_ids
from utils.argument_parser import ArgumentParser


class Meta:
    command = "#会话历史"
    description = "查看当前正在进行的会话的所有历史记录"

async def session_history_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=session_history_verify, level=normal_order_level, check_prefix=False)
async def session_history(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    gpt_session = gpt_sessions.get(data.channel_id, None)
    if gpt_session is None:
        return Chain(data).text("当前没有任何ChatGPT会话，使用\"#开始会话\"来开启一个新的ChatGPT会话。")

    # preview = [conversation['message']['content'] for conversation in gpt_session.get_conversations_group()[:4]]
    node_list = [
        {
            "senderId": sender_ids['system'],
            "time": int(gpt_session.get_start_time()),
            "senderName": "system",
            "messageChain": [
                {
                    "type": "Plain",
                    "text": "[实验功能]以下是该轮会话已经产生的对话"
                }
            ]
        },
        {
            "senderId": sender_ids['developer'],
            "time": int(gpt_session.get_start_time()),
            "senderName": "developer",
            "messageChain": [
                {
                    "type": "Plain",
                    "text": "当前系统指令仍在优化当中，如果您有更好的意见，欢迎进行反馈！"
                }
            ]
        }
    ]

    for conversation in gpt_session.get_conversations_group():
        node_list.append(
            {
                "senderId": sender_ids[conversation['message']['role']],
                "time": int(conversation['send_time']),
                "senderName": conversation['message']['role'],
                "messageChain": [
                    {
                        "type": "Plain",
                        "text": conversation['message']['content']
                    }
                ]
            }
        )

    original_message = {
        "type": "Forward",
        "display": {
            "title": f"会话记录",
            "brief": f"群{data.channel_id}于{time.strftime('%m月%d日 %H:%M', time.localtime(gpt_session.get_start_time()))}产生的会话记录",
            "source": "会话记录",
            "preview": ["点击查看", f"群 {data.channel_id} 于 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(gpt_session.get_start_time()))} 产生的会话记录"],
            "summary": f"查看{gpt_session.get_conversations_count()}条会话记录"
        },
        "nodeList": node_list
    }

    return Chain(data).extend(original_message)
