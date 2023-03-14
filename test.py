# 测试接口
from amiyabot import Message, Chain

from configs import bot, order_level, owner_qq


class Test:
    command = "#测试"


async def request_website_verify(data: Message):
    return True if data.text.startswith(Test.command) else None
@bot.on_message(verify=request_website_verify, level=order_level, check_prefix=False)
async def request_website(data: Message):
    if data.user_id != owner_qq:
        return Chain(data).text('你没有权限使用测试命令！')


