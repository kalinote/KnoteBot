from configs import bot
from amiyabot import Message

# 在进行功能筛选前将数据保存到数据库
@bot.handler_middleware
async def chat_persistence(data: Message):
    return data