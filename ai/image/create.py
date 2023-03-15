import hashlib
import json

import requests

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

    def call(self):
        try:
            ret = requests.post(
                url=ImageGeneration.url,
                headers=headers,
                data=json.dumps(self.get_data()),
                proxies=proxies
            ).text
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

    def download_images(self):
        if not self.urls:
            return False
        filenames = []
        try:
            for url in self.urls:
                ret = requests.get(url=url, proxies=proxies)
                if ret.status_code != 200:
                    del ret
                    return False

                filename = str(hashlib.md5(ret.content).hexdigest()) + '.png'
                with open(f'{image_dir}/{filename}', 'wb') as f:
                    f.write(ret.content)
                filenames.append(filename)
            return filenames
        except Exception as e:
            log.error(f"在下载生成的图片时发生了错误: {e}")
            return False
