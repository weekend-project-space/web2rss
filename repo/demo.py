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
    root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    def parserItem(entry):
        link = root_domain+entry.find('a')['href']
        title = entry.find('h2').text.strip()
        pub_date_text = entry.find('time').text.strip()
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
    return PyRSS2Gen.RSS2(
        title="Weekend Project",
        link=url,
        description="Weekend Project 的 RSS 订阅",
        lastBuildDate=datetime.now(),
        generator="web2rss",
        items=items
    )
