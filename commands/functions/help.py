import argparse
import shlex

from amiyabot import Message, Chain, log

from configs import order_level, bot, bot_name, help_doc
from utils.ArgumentParser import ArgumentParser


class Meta:
    command = "#使用说明"
    description = f"{bot_name} 的使用方法说明"

async def help_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=help_verify, level=order_level, check_prefix=False)
async def draw(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    return Chain(data).markdown(help_doc)
