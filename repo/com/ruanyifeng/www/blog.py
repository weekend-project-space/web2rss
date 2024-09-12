from support.fetch import fetch
import PyRSS2Gen
from datetime import datetime


# 定义 RSS 生成函数
def parser(url='https://ruanyifeng.com/blog', config=None):
    soup = fetch(url)

    def parserItem(entry):
        link = entry.find('a')
        title = link.text.strip()
        pub_date_text = entry.text.split('»')[0].strip()
        link_url = link['href']
        try:
            pub_date = datetime.strptime(pub_date_text, '%Y年%m月%d日')
        except ValueError:
            pub_date = datetime.now()
        return PyRSS2Gen.RSSItem(
            title=title,
            link=link_url,
            description=title,
            pubDate=pub_date
        )
    items = map(parserItem, soup.select('#homepage ul li'))
    rss = PyRSS2Gen.RSS2(
        title="阮一峰的网络日志",
        link=url,
        description="阮一峰博客的 RSS 订阅",
        lastBuildDate=datetime.now(),
        generator="web2rss",
        items=items
    )
    return rss
