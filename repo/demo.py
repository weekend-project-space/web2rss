from support.fetch import fetch
import PyRSS2Gen
from datetime import datetime
from urllib.parse import urlparse, urljoin


# 定义 RSS 生成函数
def parser(url='{url}', config=None):
    # 直接抓取成 soup 格式
    soup = fetch(url)

    # 使用 urlparse 来解析 URL 并获取根域名
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

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
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'] if description_tag else "无描述"
    return PyRSS2Gen.RSS2(
        title=title,  # 此处是网站标题
        link=url,
        description=description,  # 此处是网站描述
        lastBuildDate=datetime.now(),
        generator="web2rss",
        items=items
    )
