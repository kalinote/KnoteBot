import time

import aiohttp
from aiohttp import TCPConnector

from ai.gpt.chatgpt import ChatGPT
from commands.tasks.prompts import *
from configs import headers, proxies
from exceptions.throw_message import ThrowMessage
from amiyabot import log

async def create_embedding_with_ada(text):
    """Create an embedding with text-ada-002 using the OpenAI SDK"""
    num_retries = 10
    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
            try:
                async with session.post(
                        url=ChatGPT.url,
                        headers=headers,
                        data=json.dumps(
                            {
                                "model": "text-embedding-ada-002",
                                "input": text
                            }
                        ),
                        proxy=proxies['https']
                ) as response:
                    ret = await response.text()
                    # print(ret)
                    ret_json = json.loads(ret)

                    return ret_json["data"][0]["embedding"]
            except Exception as e:
                log.error(f"API request faild: {e}. Waiting {backoff} seconds to retry...")

        time.sleep(backoff)

async def fix_json_by_gpt(json_string):
    """
    通过GPT修复Json为可解析的回答的格式
    :param json_string:
    :return:
    """
    description_string = Prompt(
        "你需要分析用户发送的内容，并且回复python的json.loads可以解析的json内容，回复的语言使用中文，"
        "仅回复json，不带任何包括markdown格式在内的其他内容，回复如下格式：\n"
        + json.dumps(PromptGenerator.response_format, indent=4),
        "json字符串修复提示词"
    )

    # 转为markdown的json代码格式
    if not json_string.startswith("`"):
        json_string = "```json\n" + json_string + "\n```"

    try:
        result = await ChatGPT(temperature=0, system_order=description_string).call(json_string)
    except Exception as e:
        raise ThrowMessage(f"尝试修复GPT返回格式失败，错误信息: {e}")

    try:
        result_json = json.loads(result)
        return result_json
    except Exception as e:
        raise ThrowMessage(
            f"尝试修复GPT返回格式失败，错误信息: {e}\n"
            f"Task Agent返回内容: {json_string}"
            f"FixJson Agent返回内容: {result}"
        )
