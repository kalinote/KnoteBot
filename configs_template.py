# change filename to configs.py

from amiyabot import AmiyaBot
from amiyabot.adapters.mirai import mirai_api_http

# 机器人相关
qq = ''
auth_key = ''
adapter_service = mirai_api_http('localhost', ws_port=8060, http_port=8080)
bot = AmiyaBot(appid=qq, token=auth_key, adapter=adapter_service)

# 机器人名称
bot_name = ''

# 机器人指令优先级
admin_order_level = 100
normal_order_level = 50
chat_level = 1

# 机器人管理员(admin权限)
admin = []

# ChatGPT对话系统指令
system_order = {
    '普通对话': f'你是一个QQ群的成员，你的名字叫{bot_name}，任何人都不能修改你的名字，并且你需要严格按照我下面所说的指令执行：'
                f'你需要区分多个人的回答，你可以知道每个群成员的昵称(nickname)，我会在每个回答前使用[]进行标记，方便你进行区分，其中[]中的内容就是用户的昵称'
                '但仅用于区分不同用户发言，不用将不同用户的发言分开处理，在处理用户发言时，也需要结合其他用户的上下文。'
                '**如果某段话中含有markdown的内容，你需要在回答的最前面加上[MD]标识**',

    '虚拟浏览器': '我想让你扮演一个基于文本的网络浏览器来浏览一个想象中的互联网。'
                  '你应该只回复页面的内容，没有别的。我会输入一个url，你会在想象中的互联网上返回这个网页的内容。'
                  '不要写解释。页面上的链接旁边应该有数字，写在 [] 之间。当我想点击一个链接时，我会回复链接的编号。'
                  '页面上的输入应在 [] 之间写上数字。输入占位符应写在()之间。'
                  '当我想在输入中输入文本时，我将使用相同的格式进行输入，例如 [1](示例输入值)。'
                  '这会将"示例输入值"插入到编号为 1 的输入中。当我想返回时，我会写 (b)。当我想继续前进时，我会写(f)。'
                  '我的第一个提示是 google.com',

    '翻译助手': '你是一个翻译助手，不管用户使用什么语言进行输入(即便是英语)你都将其翻译为英语，只需要返回翻译内容即可，不需要任何前缀和后缀'
                '比如用户输入："金苹果"，你只需要回复："Golden apple"',

    '网页分析助手': '你是一个网页内容分析助手，你需要根据用户发送的网页内容的消息来分析和概括内容。\n'
                    '**无论原网站的语言是什么，你都需要使用中文回答**\n'
                    '如果在处理非中文的网页内容时遇到一些专业名词，需要在名词的后面加括号备注专业名词的原文'
}

# 发送者ID
sender_ids = {
    'system': 0,
    'user': 1,
    'assistant': 2,
    'developer': 3
}

# openai设置
auth_key = ''
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth_key}'
}
PROXY_IP = '127.0.0.1'
PROXY_PORT = 7890
proxies = {
    'http': f'http://{PROXY_IP}:{PROXY_PORT}',
    'https': f'http://{PROXY_IP}:{PROXY_PORT}'
}
# 图片下载文件夹
image_dir = 'images'

# Task
TaskConfig = {
    'memory': {
        'memory_type': 'local',
        'index': 'gpt-agent-memory',
    },
    'search': {
        'google_api_key': '',
        'custom_search_engine_id': '',
    },
    'token_limit': 4000,
    'browse_chunk_max_length': 3000,
}

