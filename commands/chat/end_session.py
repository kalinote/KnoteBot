import argparse
import shlex
import time

from amiyabot import Chain, log
from amiyabot import Message
from configs import order_level, bot, sender_ids
from ai.gpt.chatgpt import gpt_sessions

class EndSession:
    command = "#结束会话"
    description = "结束一个群内的任何类型的会话"

# 结束会话
async def end_session_verify(data: Message):
    return True if data.text.startswith(EndSession.command) else False
@bot.on_message(verify=end_session_verify, level=order_level, check_prefix=False)
async def end_session(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=EndSession.command, description=EndSession.description, exit_on_error=False)

    # 帮助信息
    parameters = shlex.split(data.text)[1:]
    if '-h' in parameters:
        return Chain(data).text(parser.format_help())

    # 解析命令
    try:
        args = parser.parse_args(args=parameters)
    except Exception as e:
        log.error(f"解析命令出现问题: {e}, 命令原文为: {data.text}")
        return Chain(data).text(
            f'在解析命令时出现了错误: {e}, 需要注意的是，如果参数字符串中出现了空格，需要使用引号括起来，如: "this is a example"')

    # 判断是否有会话正在进行
    gpt_session = gpt_sessions.get(data.channel_id, None)
    if gpt_session is None:
        return Chain(data).text("当前没有任何ChatGPT会话，使用\"开始对话\"来开启一个新的ChatGPT会话。")

    await bot.send_message(Chain().at(data.user_id).text(f"对话结束，销毁ChatGPT会话，本次对话共 {gpt_sessions.get(data.channel_id).get_conversations_count()} 次(包括系统和GPT回答)，总共使用 {gpt_sessions.get(data.channel_id).get_tokens_count()} Tokens。"), channel_id=data.channel_id)

    # preview = [conversation['message']['content'] for conversation in gpt_session.get_conversations_group()[:4]]
    node_list = [
        {
            "senderId": sender_ids['system'],
            "time": int(gpt_session.get_start_time()),
            "senderName": "system",
            "messageChain": [
                {
                    "type": "Plain",
                    "text": "[实验功能]会话已结束，以下是该轮会话已经产生的对话"
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
            "preview": ["会话已结束", "点击查看", f"群 {data.channel_id} 于 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(gpt_session.get_start_time()))} 产生的会话记录"],
            "summary": f"查看{gpt_session.get_conversations_count()}条会话记录"
        },
        "nodeList": node_list + [
            {
                "senderId": sender_ids['system'],
                "time": int(time.time()),
                "senderName": 'system',
                "messageChain": [
                    {
                        "type": "Plain",
                        "text": f"对话结束，本次对话共 {gpt_sessions.get(data.channel_id).get_conversations_count()} 次(包括系统和GPT回答)，总共使用 {gpt_sessions.get(data.channel_id).get_tokens_count()} Tokens。"
                    }
                ]
            }
        ]
    }

    gpt_sessions[data.channel_id] = None
    return Chain(data).extend(original_message)