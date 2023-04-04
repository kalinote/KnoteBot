from utils.argument_parser import ArgumentParser

from amiyabot import Chain
from amiyabot import Message

from commands.chat import end_session
from configs import system_order, bot_name, normal_order_level, bot
from ai.gpt.chatgpt import ChatGPT
from ai.gpt.chatgpt import gpt_sessions

class Meta:
    command = "#会话"
    description = "开始一段会话，每个群只能同时开启一个单独的会话(除单次会话外)"

# 普通会话模式
async def start_session_verify(data: Message):
    return True if data.text.startswith(Meta.command) else False
@bot.on_message(verify=start_session_verify, level=normal_order_level, check_prefix=False)
async def start_session(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 添加选项和参数
    parser.add_argument('-t', '--temperature', type=float, default=0.7, help="ChatGPT的temperature值，为0-1之间的浮点数，该值越高(如0.8)将使输出更随机，而越低(例如0.2)将使其更集中和更确定，默认值0.7")
    parser.add_argument('-so', '--system-order', type=str, help="开始对话前的系统指令，用于指示该轮会话ChatGPT所扮演的角色或需要做的事，越详细越好，默认值为系统预置的普通对话系统指令")
    parser.add_argument('-no', '--no-order', action='store_true', help="是否不设置系统指令，如果指定该参数，则不设置任何系统指令(包括默认系统指令)")
    parser.add_argument('-s', '--single', action='store_true', help="是否为单句会话模式，如果指定该参数，则只进行一次问答，且不能设置系统指令(-so和--system-order参数无效)。")
    parser.add_argument('-p', '--prompt', type=str, default=None, help="对话提示词，在单句会话模式中使用，如果是单次会话模式(指定-s或者--single参数)，则参数必须指定，否则指定该参数无效。")
    parser.add_argument('-u', '--user', action='store_true', help="是否在聊天前添加[username]来对用户进行区分，如果指定该参数，则添加用户名区分。在使用默认系统指令的连续会话时会自动指定，其他情况均不会自动指定。")

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    temperature = args.temperature
    no = args.no_order
    single = args.single
    prompt = args.prompt
    user = args.user
    order = args.system_order
    if not single:
        if not no:
            if not args.system_order:
                order = system_order['普通对话']
                user = True
            else:
                order = args.system_order
        else:
            order = None

    # 先处理单句会话
    if single:
        if prompt is None:
            return Chain(data).text("使用单次会话模式时(指定-s或者--single参数)，必须通过-p或者--prompt参数来指定提示词。\n详细使用方法请使用-h或--help参数查询。")
        return Chain(data).text(ChatGPT(temperature=temperature, system_order=None, set_user=user).call(content=(f"[{data.nickname}]" if user else '') + prompt))

    if gpt_sessions.get(data.channel_id, None) is not None:
        return Chain(data).text(f"上一次会话尚未结束，或结束后为及时清理会话，请使用\"{end_session.Meta.command}\"来清除当前会话，并使用\"{Meta.command}\"来开启一个新的ChatGPT会话。")

    gpt_sessions[data.channel_id] = ChatGPT(temperature=temperature, system_order=order, set_user=user)
    return Chain(data).text("\n\n新建ChatGPT会话，现在可以开始对话了。\n\n"
                            f"在会话过程中，如果你发送的内容不是想对{bot_name}说的，可以在发言内容前面加*，{bot_name}将不会看到这条消息\n\n"
                            f"[实验功能]在会话过程中，如果你想对{bot_name}说，但不想得到{bot_name}的回复，可以在发言内容前面加\"-\"，{bot_name}可以看到这条消息，但不会回复。\n\n"
                            f"对话完成后，使用\"{end_session.Meta.command}\"指令来结束对话。")
