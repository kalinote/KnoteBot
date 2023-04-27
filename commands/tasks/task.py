import shlex

from amiyabot import Chain, log
from amiyabot import Message

from ai.gpt.chatgpt import ChatGPT
from configs import normal_order_level, image_dir, bot, system_order, bot_name
from ai.image.create import ImageGeneration
from utils.argument_parser import ArgumentParser
from commands.tasks.prompts import *

class Meta:
    command = "#任务"
    description = f"指定一个(或多个，可能未来支持)任务，由{bot_name}自动完成。"

# 自动执行任务
async def auto_task_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=auto_task_verify, level=normal_order_level, check_prefix=False)
async def auto_task(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 添加选项和参数
    parser.add_argument('-r', '--role', type=str, required=True, help=f"设置{bot_name}需要扮演的角色")
    parser.add_argument('-g', '--goal', type=str, required=True, help=f"设置需要由{bot_name}完成的目标")


    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    role = args.role
    goal = args.goal

    # 创建一个main提示词生成器(目标应该是一个list，包含所有阶段的目标，现在暂时先定一个)
    # main_prompt_generator = PromptGenerator(role=role, goals=[goal])
    return Chain(data).text(str(PromptGenerator(role=role, goals=[goal]).init_prompt_string))

