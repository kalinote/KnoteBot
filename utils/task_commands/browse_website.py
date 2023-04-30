import spacy
from playwright.async_api import async_playwright, Error
from bs4 import BeautifulSoup
from requests.compat import urljoin

from ai.gpt.chatgpt import ChatGPT
from ai.gpt.utils import count_message_tokens
from commands.tasks.memory import get_memory
from configs import TaskConfig

from amiyabot import log

MEMORY = get_memory()

def token_usage_of_chunk(messages, model):
    return count_message_tokens(messages, model)

def split_text(
        text: str,
        max_length: int = TaskConfig['browse_chunk_max_length'],
        model: str = 'gpt-3.5-turbo',
        question: str = ""):
    """
    分割文本到指定长度
    """
    flatened_paragraphs = " ".join(text.split("\n"))
    nlp = spacy.load('zh_core_web_sm')
    nlp.add_pipe("sentencizer")
    doc = nlp(flatened_paragraphs)
    sentences = [sent.text.strip() for sent in doc.sents]

    current_chunk = []

    for sentence in sentences:
        message_with_additional_sentence = [
            create_message(" ".join(current_chunk) + " " + sentence, question)
        ]

        expected_token_usage = (
            token_usage_of_chunk(messages=message_with_additional_sentence, model=model)
            + 1
        )
        if expected_token_usage <= max_length:
            current_chunk.append(sentence)
        else:
            yield " ".join(current_chunk)
            current_chunk = [sentence]
            message_this_sentence_only = [
                create_message(" ".join(current_chunk), question)
            ]
            expected_token_usage = (
                token_usage_of_chunk(messages=message_this_sentence_only, model=model)
                + 1
            )
            if expected_token_usage > max_length:
                raise ValueError(
                    f"Sentence is too long in webpage: {expected_token_usage} tokens."
                )

    if current_chunk:
        yield " ".join(current_chunk)

def create_message(chunk: str, question: str):
    """
    创建ChatGPT对话格式的信息
    """
    return {
        "role": "user",
        "content": f'"""{chunk}""" 请使用上述文本回答以下问题："{question}" -- 如果问题无法使用文本回答，请总结文本。',
    }

async def summarize_text(url: str, text: str, question: str):
    """
    合成由网页获取到的文本内容
    """
    if not text:
        return "Error: No text to summarize"

    model = 'gpt-3.5-turbo'
    text_length = len(text)

    summaries = []
    chunks = list(
        split_text(
            text, max_length=TaskConfig['browse_chunk_max_length'], model=model, question=question
        ),
    )

    for i, chunk in enumerate(chunks):
        memory_to_add = f"Source: {url}\n" f"Raw content part#{i + 1}: {chunk}"

        await MEMORY.add(memory_to_add)

        messages = [create_message(chunk, question)]
        tokens_for_chunk = count_message_tokens(messages, model)
        log.info(
            f"正在对第 {i + 1} / {len(chunks)} 段文本进行总结，长度为 {len(chunk)} 个字符，或 {tokens_for_chunk} 个标记"
        )

        gpt = ChatGPT(temperature=0, using_model=model)
        for message in messages:
            gpt.add_conversation(role=message['role'], content=message['content'])
        # log.debug(str(gpt.get_conversations_group()))
        summary = await gpt.call()
        summaries.append(summary)
        log.info(
            f"已将第 {i + 1} 段文本的总结添加到内存中，长度为 {len(summary)} 个字符"
        )

        memory_to_add = f"Source: {url}\n" f"Content summary part#{i + 1}: {summary}"

        await MEMORY.add(memory_to_add)

    log.info(f"已总结 {len(chunks)} 段文本。")

    combined_summary = "\n".join(summaries)
    messages = [create_message(combined_summary, question)]

    gpt = ChatGPT(temperature=0, using_model=model)
    for message in messages:
        gpt.add_conversation(role=message['role'], content=message['content'])
    # log.debug(str(gpt.get_conversations_group()))
    return await gpt.call()


def extract_hyperlinks(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
    """
    从 BeautifulSoup 对象中提取超链接
    """
    return [
        (link.text, urljoin(base_url, link["href"]))
        for link in soup.find_all("a", href=True)
    ]


def format_hyperlinks(hyperlinks: list[tuple[str, str]]) -> list[str]:
    """
    格式化要显示给用户的超链接
    """
    return [f"{link_text} ({link_url})" for link_text, link_url in hyperlinks]

async def browse_website(url: str, question: str):
    """
    获取链接中的内容
    """
    text = await scrape_text_with_playwright(url)
    summary_text = await summarize_text(url, text, question)
    links = await scrape_links_with_playwright(url)

    # Limit links to 5
    if len(links) > 5:
        links = links[:5]
    return f"Answer gathered from website: {summary_text} \n \n Links: {links}"

async def scrape_text_with_playwright(url: str):
    """
    通过async_playwright获取网页内容
    """
    async with async_playwright() as p:
        browser_type = p.chromium  # 可替换为 p.firefox 或 p.webkit

        # 更多配置可以参考: https://playwright.dev/python/docs/api/class-browsertype#browsertype_launch
        browser = await browser_type.launch(headless=True)
        context = await browser.new_context()

        # 可以在这里设置更多上下文选项, 如 user_agent
        # 参考: https://playwright.dev/python/docs/api/class-browser#browser_new_context
        page = await context.new_page()
        try:
            await page.goto(url)
            page_source = await page.content()
            soup = BeautifulSoup(page_source, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

        except Error as e:
            print(f"Error: {e}")

        finally:
            await browser.close()
            return text

async def scrape_links_with_playwright(url: str):
    """
    通过async_playwright获取网页中的链接
    """
    async with async_playwright() as p:
        browser_type = p.chromium  # 可替换为 p.firefox 或 p.webkit

        browser = await browser_type.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url)
            page_source = await page.content()
            soup = BeautifulSoup(page_source, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            hyperlinks = extract_hyperlinks(soup, url)  # 请确保 extract_hyperlinks 函数已经定义
            formatted_hyperlinks = format_hyperlinks(hyperlinks)  # 请确保 format_hyperlinks 函数已经定义

        except Error as e:
            print(f"Error: {e}")

        finally:
            await browser.close()
            return formatted_hyperlinks
