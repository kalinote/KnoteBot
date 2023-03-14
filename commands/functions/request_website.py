import argparse
import shlex

from amiyabot import Chain, log
from amiyabot import Message
from configs import order_level, bot

class RequestWebsite:
    command = "#请求网站"
    description = "请求指定链接网站，并渲染主页生成图片\n该功能尚处于实验阶段，可能不稳定，建议不要频繁使用。"

# 请求网站
async def request_website_verify(data: Message):
    return True if data.text.startswith(RequestWebsite.command) else None
@bot.on_message(verify=request_website_verify, level=order_level, check_prefix=False)
async def request_website(data: Message):
    # 解析参数
    parser = argparse.ArgumentParser(prog=RequestWebsite.command, description=RequestWebsite.description)

    # 添加选项和参数
    parser.add_argument('-u', '--url', type=str, default="https://kalinote.top/", help="需要请求的网站url，使用美国代理，在请求部分国内网站时可能出现问题，默认为kalinote.top")

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

    url = args.url

    await bot.send_message(Chain().at(data.user_id).text("[实验功能]正在请求并绘制网站内容，该过程需要6秒左右，请稍等..."), channel_id=data.channel_id)

    return Chain(data).html(url, is_template=False, render_time=6000)

