from amiyabot import Message, Chain
from playwright.async_api import async_playwright

from configs import normal_order_level, bot, PROXY_IP, PROXY_PORT
from utils.argument_parser import ArgumentParser


async def get_tags(data):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={
                "server": f"{PROXY_IP}:{PROXY_PORT}",
                "username": "",
                "password": ""
            }
        )

        page = await browser.new_page()
        await page.goto("https://www.pixiv.net/tags", wait_until="load")

        screenshot_bytes = await page.screenshot(full_page=True)
        await bot.send_message(Chain().image(screenshot_bytes), channel_id=data.channel_id)

        tags = await page.locator('//a[@class="tag-value icon-text"]').all()
        tags_text = ''
        count = 0
        for tag in tags[:100]:
            count+=1
            tags_text += f"{count}. {await tag.inner_text()}\n"

        return tags_text

class Meta:
    command = "#pixiv"
    description = f"pivix操作指令，详细说明使用 #pixiv -h/--help 或 #pixiv help 指令查看"


async def pixiv_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=pixiv_verify, level=normal_order_level, check_prefix=False)
async def pixiv(data: Message):
    parent_parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # gettags
    gettags_parser = parent_parser.add_subparsers(dest="sub_command")
    gettags_parser.add_parser('gettags', help='获取热门pixiv标签')

    # 解析命令
    try:
        args = parent_parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    if args.sub_command == 'gettags':
        return Chain(data).text("前100个Tags，按照热度从高到低排序(QQ限制发送字数，无法全部显示):\n\n" + await get_tags(data))
