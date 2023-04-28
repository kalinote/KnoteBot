import hashlib
import json

import aiohttp
from aiohttp import TCPConnector

from configs import headers, proxies, image_dir
from amiyabot import log


class ImageGeneration:
    url = 'https://api.openai.com/v1/images/generations'

    def __init__(self, prompt, gen_number=1, size="1024x1024"):
        self.gen_number = gen_number
        self.size = size
        self.prompt = prompt
        self.urls = []

    def get_data(self):
        return {
            "prompt": self.prompt,
            "n": self.gen_number,
            "size": self.size
        }

    async def call(self):
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                async with session.post(
                        url=ImageGeneration.url,
                        headers=headers,
                        data=json.dumps(self.get_data()),
                        proxy=proxies['https']
                ) as response:
                    ret = await response.text()
                    ret_json = json.loads(ret)
        except Exception as e:
            log.error(f"在请求图片时出现了错误: {e}")
            return f"在请求图片时出现了错误: {e}"
        try:
            urls = [datas['url'] for datas in ret_json['data']]
            self.urls = urls
        except Exception as e:
            log.error(f"在解析json时出现了错误: {e}, json原文: {ret_json}")
            return f"[Draw Handler]在处理json时出现错误，{e}，JSON原文为：{str(ret_json)}"
        return urls

    async def download_images(self):
        if not self.urls:
            return False
        filenames = []
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
                for url in self.urls:
                    async with session.get(url=url, proxy=proxies['https']) as response:
                        if response.status != 200:
                            return False

                        content = await response.read()
                        filename = str(hashlib.md5(content).hexdigest()) + '.png'
                        with open(f'{image_dir}/{filename}', 'wb') as f:
                            f.write(content)
                        filenames.append(filename)
            return filenames
        except Exception as e:
            log.error(f"在下载生成的图片时发生了错误: {e}")
            return False
