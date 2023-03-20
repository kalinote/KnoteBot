import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message
from playwright.async_api import async_playwright

from configs import order_level, bot, PROXY_IP, PROXY_PORT


class RequestWebsite:
    command = "#搜索"
    description = "通过搜索引擎搜索相关内容，并通过GPT进行资料整理。"

# 请求网站
async def search_verify(data: Message):
    return True if data.text.startswith(RequestWebsite.command) else None
@bot.on_message(verify=search_verify, level=order_level, check_prefix=False)
async def search_website(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=RequestWebsite.command, description=RequestWebsite.description)

    # 添加选项和参数
    parser.add_argument('-k', '--keyword', type=str, default="什么是ChatGPT", help="需要搜索的关键词，默认为\"什么是ChatGPT\"")

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

    keyword = args.keyword
    url = f"https://www.google.com/search?q={keyword}"

    await bot.send_message(Chain().at(data.user_id).text("[实验功能]正在请求搜索内容，该过程需要6秒左右，请稍等..."), channel_id=data.channel_id)
    # await bot.send_message(Chain().html(url, is_template=False, render_time=6000), channel_id=data.channel_id)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={
                "server": f"{PROXY_IP}:{PROXY_PORT}",
                "username": "",
                "password": ""
            }
        )
        page = await browser.new_page()
        await page.goto(url)
        screenshot_bytes = await page.screenshot(full_page=True)
        await bot.send_message(Chain().image(screenshot_bytes), channel_id=data.channel_id)

    return

