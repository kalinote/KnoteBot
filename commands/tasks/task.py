import json

from amiyabot import Chain
from amiyabot import Message, log

from commands.tasks.agent import Agent
from commands.tasks.utils import fix_json_by_gpt
from configs import normal_order_level, bot
from exceptions.throw_message import ThrowMessage
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

    # 创建一个代理人
    agent = Agent(role=role, goals=[goal])

    loop_count = 0
    continuous_limit = 3
    while True:
        loop_count += 1
        if loop_count > continuous_limit:
            break

        try:
            result, message = await agent.run_step(user_input="确定要使用的下一个命令，并使用上面指定的JSON格式响应，且不带其他任何格式，仅回复Json内容:")
        except ThrowMessage as msg:
            return Chain(data).text(str(msg))

        try:
            result_json = json.loads(result)
        except Exception as e:
            log.error(f'Agent返回内容解析失败:\n{e}')
            log.error(f'result: {result}')
            try:
                result_json = await fix_json_by_gpt(result)
            except Exception as err:
                return Chain(data).text(f'Agent返回内容解析失败:\n{err}')

        try:
            reply = (
                f"我的想法是: {result_json['thoughts']['text']}\n"
                f"理由是: {result_json['thoughts']['reasoning']}\n\n"
                f"为了实现这个想法，我的计划是:\n{result_json['thoughts']['plan']}\n\n"
                f"{result_json['thoughts']['criticism']}\n\n"
                f"下一步指令: {result_json['command']['name']}\n"
                f"参数: {str(result_json['command']['args'])}"
            )
        except Exception as e:
            return Chain(data).text(f'Agent返回Json解析失败:\n{e}\n\nJson内容为: {result_json}')

        # log.debug(json.dumps({'message': message}, indent=4))
        await bot.send_message(Chain().at(data.user_id).text(reply),
                               channel_id=data.channel_id)

    # await bot.send_message(Chain().at(data.user_id).text(json.dumps({'message': message}, indent=4)), channel_id=data.channel_id)
    return

