import glob
import importlib.util
import os

from amiyabot import Message, Chain

from configs import normal_order_level, bot, bot_name
from utils.argument_parser import ArgumentParser

# 生成机器人帮助文档
def get_command_meta(command_file_path):
    spec = importlib.util.spec_from_file_location(os.path.basename(command_file_path)[:-3], command_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "Meta"):
        return getattr(module, "Meta")()
    return None

class Meta:
    command = "#使用说明"
    description = f"{bot_name} 的使用方法说明"

async def help_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=help_verify, level=normal_order_level, check_prefix=False)
async def draw(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    # 生成文档
    help_doc = "# {bot_name} 使用说明\n\n".format(bot_name=bot_name)
    help_doc += f"## 聊天类:\n\n"
    for file_path in glob.glob(os.path.join("commands/chat", "*.py")):
        if os.path.basename(file_path) == '__init__.py':
            continue

        # 读取文件中的 Meta 类信息
        command_meta = get_command_meta(file_path)
        if command_meta:
            # 将 Meta 类信息插入到 help_doc 变量中
            help_doc += f"### {command_meta.command}\n{command_meta.description}\n\n"

    help_doc += f"## 功能类:\n\n"
    for file_path in glob.glob(os.path.join("commands/functions", "*.py")):
        if os.path.basename(file_path) == '__init__.py':
            continue

        # 读取文件中的 Meta 类信息
        command_meta = get_command_meta(file_path)
        if command_meta:
            # 将 Meta 类信息插入到 help_doc 变量中
            help_doc += f"### {command_meta.command}\n{command_meta.description}\n\n"

    help_doc += f"## <div style=\"color:red;\">管理员</div>\n\n"
    for file_path in glob.glob(os.path.join("commands/admin", "*.py")):
        if os.path.basename(file_path) == '__init__.py':
            continue

        # 读取文件中的 Meta 类信息
        command_meta = get_command_meta(file_path)
        if command_meta:
            # 将 Meta 类信息插入到 help_doc 变量中
            help_doc += f"### {command_meta.command}\n{command_meta.description}\n\n"

    help_doc += "---\n想要阅读更详细的帮助文档，使用以下命令来获取对应功能的详细文档(包括本命令):\n```shell\n#命令 -h\n```\n"

    return Chain(data).markdown(help_doc)
