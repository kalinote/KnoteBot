import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message
from playwright.async_api import async_playwright

from ai.gpt.chatgpt import ChatGPT
from configs import order_level, bot, PROXY_IP, PROXY_PORT

def get_middle_chars(s, n):
    middle = len(s) // 2
    start = middle - n // 2
    end = start + n
    return s[start:end]

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
    parser.add_argument('-k', '--keyword', type=str, default="kalinote.top", help="需要搜索的关键词，默认为\"kalinote.top\"")

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

    await bot.send_message(Chain().at(data.user_id).text("[实验功能]正在请求搜索内容，该过程需要数秒，请稍等..."), channel_id=data.channel_id)

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

        # 定位第一个 <h3> 标签的父标签并跳转
        # h3_element = await page.query_selector('h3')
        # parent_element = await h3_element.query_selector('xpath=..')
        # await page.goto(await parent_element.get_attribute('href'))

        h3_elements = await page.query_selector_all('h3')
        if not h3_elements:
            # 页面中没有h3元素
            await bot.send_message(Chain().text("出现错误，没有在google的搜索页面找到h3，请稍后或换一个关键词重试！"), channel_id=data.channel_id)
            screenshot_bytes = await page.screenshot(full_page=True)
            return Chain(data).image(screenshot_bytes)

        for h3_element in h3_elements:
            parent_element = await h3_element.query_selector('xpath=..')
            if not parent_element:
                continue
            href = await parent_element.get_attribute('href')
            if href is not None:
                # 找到具有href属性的父元素
                await page.goto(href)
                break


        screenshot_bytes = await page.screenshot(full_page=True)
        await bot.send_message(Chain().image(screenshot_bytes), channel_id=data.channel_id)

        # content = await page.inner_text('h1, p, div')
        content = await page.inner_text('body')

    reply = ''
    gpt = ChatGPT(temperature=0.3, system_order="你是一个网页内容分析助手，你需要根据用户发送的网页内容的消息来分析")

    if len(content) > 3500:
        reply += f'[由于ChatGPT API限制，只能识别3500个字符(4097 token)，但本篇文章全长共{len(content)}字符]\n[3500个字符是截取网页最中间的，最大程度减小顶部链接或底部链接对内容分析的影响]\n'
        content = get_middle_chars(content, 3500)

    # print(content)
    gpt.add_conversation('user', content)
    reply += gpt.call('请对以上内容进行分析，并使用中文描述')

    return Chain(data).text(reply)

