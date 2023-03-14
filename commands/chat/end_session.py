import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message
from configs import order_level, bot
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
    parser = argparse.ArgumentParser(prog=EndSession.command, description=EndSession.description)

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

    if gpt_sessions.get(data.channel_id, None) is None:
        return Chain(data).text("当前没有任何ChatGPT会话，使用\"开始对话\"来开启一个新的ChatGPT会话。")

    answer = f"对话结束，销毁ChatGPT会话，本次对话共 {gpt_sessions.get(data.channel_id).get_conversations_count()} 次(包括系统和GPT回答)，总共使用 {gpt_sessions.get(data.channel_id).get_tokens_count()} Tokens。"
    gpt_sessions[data.channel_id] = None
    return Chain(data).text(answer)