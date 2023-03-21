from playwright.async_api import Playwright, Browser
from amiyabot import BrowserLaunchConfig

from configs import PROXY_IP, PROXY_PORT


class ChromeBrowserLauncher(BrowserLaunchConfig):
    def __init__(self):
        super().__init__()

    # 继承并改写 launch_browser 方法
    async def launch_browser(self, playwright: Playwright) -> Browser:
        # 返回通过任意方式创建的 Browser 对象
        return await playwright.chromium.launch(
            proxy={
                "server": f"{PROXY_IP}:{PROXY_PORT}",
                "username": "",
                "password": ""
            }
        )
