from support.fetch import fetch
from readability import Document


def _clean_attributes(soup):
    """
    删除 HTML 标签中的无用属性。
    """
    for tag in soup.find_all(True):  # 找到所有标签
        # 去除特定的无用属性，例如 'id', 'class', 'style', 'onclick' 等
        for attribute in ['id', 'class', 'style', 'onclick']:
            if attribute in tag.attrs:
                tag.attrs.pop(attribute, None)


def _clean_empty_tag(soup):
    """
    删除 HTML 中的无用标签。
    """
    for tag in soup.find_all(True):
        # 去掉空标签，检查是否只有空格或换行符
        if not tag.text.strip():
            tag.decompose()  # 删除标签及其内容


def url2maincontent(url):
    soup = fetch(url)
    # 去除不需要的部分（例如广告、导航、页脚）
    # 删除所有 script 和 style 标签
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    # 去除不需要的部分，排除广告、页眉、页脚等
    for selector in ['.header', '.footer', '.advertisement', '#sidebar']:
        for element in soup.select(selector):
            element.decompose()
    # 清理标签属性
    _clean_attributes(soup)
    _clean_empty_tag(soup)
    # 尝试提取正文内容
    main_content = soup.find('main') or soup.find('article') or\
        soup.find('div', class_='content')
    if main_content:
        return main_content.prettify()
    else:
        doc = Document(soup.find('body').prettify())
        return doc.summary()
