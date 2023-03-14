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
    parser = argparse.ArgumentParser(prog=Help.command, description=Help.description)

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

    return Chain(data).markdown(help_doc)
