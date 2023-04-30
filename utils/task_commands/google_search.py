import json

import aiohttp
from aiohttp import TCPConnector

from configs import TaskConfig, proxies
from exceptions.throw_message import ThrowMessage

from amiyabot import log

async def google_search_by_api(query, num_results=8):
    """
    通过API进行搜索
    :param query:
    :param num_results:
    :return:
    """
    try:
        # Get the Google API key and Custom Search Engine ID from the config file
        api_key = TaskConfig.get('search', {}).get('google_api_key', None)
        custom_search_engine_id = TaskConfig.get('search', {}).get('custom_search_engine_id', None)

        async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.get(
                url=f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={custom_search_engine_id}&num={num_results}",
                proxy=proxies['https']
            ) as resp:
                response_text = await resp.text()

        # Extract the search result items from the response
        result = json.loads(response_text)
        search_results = result.get("items", [])

        # Create a list of only the URLs from the search results
        search_results_links = [item["link"] for item in search_results]

    except Exception as e:
        # Handle errors in the API call
        log.error(f"执行google搜索发生错误: {e}")
        raise ThrowMessage(f"执行google搜索发生错误: {e}")

    # Return the list of search result URLs
    return search_results_links


async def google_search_by_browser(query, num_results=8):
    """
    通过浏览器搜索
    :param query:
    :param num_results:
    :return:
    """
    pass