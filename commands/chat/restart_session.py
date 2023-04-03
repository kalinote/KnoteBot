from amiyabot import Chain, log
from amiyabot import Message

from commands import StartSession
from configs import order_level, bot
from ai.gpt.chatgpt import gpt_sessions
from utils.ArgumentParser import ArgumentParser


class RestartSession:
    command = "#重启会话"
    description = "在一段会话的进行过程当中重新启动会话，但不重置当前会话的token使用情况"

# 重启会话
async def restart_session_verify(data: Message):
    return True if data.text.startswith(RestartSession.command) else False
@bot.on_message(verify=restart_session_verify, level=order_level, check_prefix=False)
async def start_session(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=RestartSession.command, description=RestartSession.description, exit_on_error=False)

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    if gpt_sessions.get(data.channel_id, None) is None:
        return Chain(data).text(f"当前没有进行当中的会话，请使用\"{StartSession.command}\"来开启一个新的ChatGPT会话。")

    gpt_sessions[data.channel_id].restart()
    return Chain(data).text(f"本轮会话已重置，当前使用token为: {gpt_sessions[data.channel_id].get_tokens_count()}")
