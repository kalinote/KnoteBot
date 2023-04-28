from amiyabot import Chain
from amiyabot import Message
from configs import bot, chat_level
from ai.gpt.chatgpt import gpt_sessions

# ChatGPT
async def gpt_verify(data: Message):
    # 过滤掉以*开始的消息，作为停止词
    if data.text.startswith('*'):
        return None
    return True if gpt_sessions.get(data.channel_id, None) is not None else None
@bot.on_message(verify=gpt_verify, level=chat_level)
async def gpt(data: Message):
    if data.text.startswith("-"):
        gpt_sessions.get(data.channel_id).add_conversation('user', f"[{data.nickname}]{data.text[1:]}")
        return

    chat_gpt = gpt_sessions.get(data.channel_id)

    answer = await chat_gpt.call((f"[{data.nickname}]" if chat_gpt.get_set_user() else '') + data.text)

    alarm = gpt_sessions.get(data.channel_id).tokens_usage_check()
    if alarm:
        await bot.send_message(Chain().text(f"[Alarm]当前会话已进行{gpt_sessions.get(data.channel_id).get_conversations_count()}次，Token已使用数量为: {alarm}，请注意控制用量"), channel_id=data.channel_id)

    # 处理markdown
    if answer.startswith('[MD]'):
        return Chain(data).markdown(answer)
    else:
        return Chain(data).text(answer)
