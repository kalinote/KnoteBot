import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message

from commands import StartSession
from configs import order_level, bot
from ai.gpt.chatgpt import gpt_sessions

class RestartSession:
    command = "#重启会话"
    description = "在一段会话的进行过程当中重新启动会话，但不重置当前会话的token使用情况"

# 重启会话
async def restart_session_verify(data: Message):
    return True if data.text.startswith(RestartSession.command) else False
@bot.on_message(verify=restart_session_verify, level=order_level, check_prefix=False)
async def start_session(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=RestartSession.command, description=RestartSession.description, exit_on_error=False)

    # 在解析命令前先把-h处理掉，不然会导致程序退出
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
        return Chain(data).text(f"当前没有进行当中的会话，请使用\"{StartSession.command}\"来开启一个新的ChatGPT会话。")

    gpt_sessions[data.channel_id].restart()
    return Chain(data).text(f"本轮会话已重置，当前使用token为: {gpt_sessions[data.channel_id].get_tokens_count()}")
