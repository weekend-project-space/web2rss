import requests
import json
from support.config import get_item
from support.fetch import fetch


def gen_code_chat(messages):
    messages.append({"role": "assistant", "content":
                     _chat(messages)})
    return messages


def gen_code(url):
    content = fetch(url, 'text')
    # print(content)
    prompt = __gen_prompts(content, url)
    messages = [{
        "role": "system",
        "content": "现在你是一个python程序员，只负责写代码不提供其他说明介绍"
    }, {
        "role": "user",
        "content": prompt
    }]
    return gen_code_chat(messages)


def _chat(messages, api_url='', api_key=''):

    key = api_key or get_item('gpt_api_key')
    # 请求头信息，包含 API 密钥和内容类型
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    }

    # GPT 模型的请求数据
    data = {
        "model": "gpt-4o-mini",  # 模型引擎，也可以选择 gpt-4
        "messages": messages,  # 输入的提示信息
        "max_tokens": 2000,  # 返回的最大字数
        "temperature": 0.7  # 文本生成的随机性
    }

    # OpenAI API 的 URL
    url = api_url or get_item('gpt_api_url')
    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 检查请求是否成功
    if response.status_code == 200:
        # print(response.json())
        # 提取 GPT 生成的文本
        gpt_response = response.json()['choices'][0]['message']['content']\
            .strip()
        return gpt_response
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)
        raise RuntimeError(response.text)


def __gen_prompts(html, url):
    return f"""
        "{html}"
        请把这个网页用python转换成rss 这是一个python代码示例，不需要调整代码结构，
        只调整代码里面的取item的逻辑即可， 只给出代码
        ``` py
        from support.fetch import fetch
        import PyRSS2Gen
        from datetime import datetime
        from urllib.parse import urlparse


        # 定义 RSS 生成函数
        def parser(url='{url}', config=None):
            # 直接抓取成 soup 格式
            soup = fetch(url)

            # 使用 urlparse 来解析 URL 并获取根域名
            parsed_url = urlparse(url)
            base_url = parsed_url.scheme+"://"+parsed_url.netloc

            def parserItem(entry):
            # 转换为绝对地址
            link = urljoin(base_url, entry.find('a')['href'])
            title_tag = entry.find('h2')
            title = title_tag.text.strip() if title_tag else '没有标题'
            date_tag = entry.find('time')
            pub_date_text = date_tag.text.strip() if date_tag else '-'
            try:
                pub_date = datetime.strptime(pub_date_text, '%Y-%m-%d')
            except ValueError:
                pub_date = datetime.now()
            return PyRSS2Gen.RSSItem(
                title=title,
                link=link,
                description=title,
                pubDate=pub_date
            )
        items = map(parserItem, soup.select('main section'))

        # 获取标题
        title = soup.title.string if soup.title else "无标题"

        # 获取描述
        description_tag = soup.find('meta', attrs={{'name': 'description'}})
        description = description_tag['content'] if description_tag else "无描述"

        return PyRSS2Gen.RSS2(
            title=title,  # 此处是网站标题
            link=url,
            description=description,  # 此处是网站描述
            lastBuildDate=datetime.now(),
            generator="web2rss",
            items=items
        )


        ```
    """
