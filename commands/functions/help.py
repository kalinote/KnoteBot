import argparse
import shlex

from amiyabot import Message, Chain, log

from configs import order_level, bot, bot_name, help_doc

class Help:
    command = "#使用说明"
    description = f"{bot_name} 的使用方法说明"

async def help_verify(data: Message):
    return True if data.text.startswith(Help.command) else None
@bot.on_message(verify=help_verify, level=order_level, check_prefix=False)
async def draw(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=Help.command, description=Help.description, exit_on_error=False)

    # 帮助信息
    parameters = shlex.split(data.text)[1:]
    if '-h' in parameters or '--help' in parameters:
        return Chain(data).text(parser.format_help())

    # 解析命令
    args = parser.parse_args(args=parameters)

    return Chain(data).markdown(help_doc)
