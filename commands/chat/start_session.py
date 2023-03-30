import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message

from .end_session import EndSession
from configs import system_order, bot_name, order_level, bot
from ai.gpt.chatgpt import ChatGPT
from ai.gpt.chatgpt import gpt_sessions

class StartSession:
    command = "#会话"
    description = "开始一段会话，每个群只能同时开启一个单独的会话"

# 普通会话模式
async def start_session_verify(data: Message):
    return True if data.text.startswith(StartSession.command) else False
@bot.on_message(verify=start_session_verify, level=order_level, check_prefix=False)
async def start_session(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=StartSession.command, description=StartSession.description, exit_on_error=False)

    # 添加选项和参数
    parser.add_argument('-t', '--temperature', type=float, default=0.7, help="ChatGPT的temperature值，为0-1之间的浮点数，该值越高(如0.8)将使输出更随机，而越低(例如0.2)将使其更集中和更确定，默认值0.7")
    parser.add_argument('-so', '--system-order', type=str, default=system_order['普通对话'], help="开始对话前的系统指令，用于指示该轮会话ChatGPT所扮演的角色或需要做的事，越详细越好，默认值为系统预置的普通对话系统指令")

    # 在解析命令前先把-h处理掉，不然会导致程序退出
    parameters = shlex.split(data.text)[1:]
    if '-h' in parameters:
        return Chain(data).text(parser.format_help())

    # 解析命令
    args = parser.parse_args(args=parameters)

    temperature = args.temperature
    order = args.system_order

    if gpt_sessions.get(data.channel_id, None) is not None:
        return Chain(data).text(f"上一次会话尚未结束，或结束后为及时清理会话，请使用\"{EndSession.command}\"来清除当前会话，并使用\"{StartSession.command}\"来开启一个新的ChatGPT会话。")

    gpt_sessions[data.channel_id] = ChatGPT(temperature=temperature, system_order=order)
    return Chain(data).text("新建ChatGPT会话，现在可以开始对话了。\n"
                            f"在会话过程中，如果你发送的内容不是想对{bot_name}说的，可以在发言内容前面加*，{bot_name}将不会看到这条消息\n"
                            f"[实验功能]在会话过程中，如果你想对{bot_name}说，但不想得到{bot_name}的回复，可以在发言内容前面加\"-\"，{bot_name}可以看到这条消息，但不会回复。\n"
                            f"对话完成后，使用{EndSession.command}指令来结束对话。")
