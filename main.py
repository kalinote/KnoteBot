import asyncio

from commands import *
from browsers.chrome import ChromeBrowserLauncher

asyncio.run(bot.start(
    launch_browser=ChromeBrowserLauncher()
))

