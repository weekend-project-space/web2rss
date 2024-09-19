from support.fetch import fetch


def _clean_attributes(soup):
    """
    删除 HTML 标签中的无用属性。
    """
    for tag in soup.find_all(True):  # 找到所有标签
        # 去除特定的无用属性，例如 'id', 'class', 'style', 'onclick' 等
        for attribute in ['id', 'class', 'style', 'onclick']:
            if attribute in tag.attrs:
                tag.attrs.pop(attribute, None)


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
    # 尝试提取正文内容
    main_content = soup.find('main') or soup.find('article') or\
        soup.find('div', class_='content')
    if main_content:
        return main_content.prettify()
    else:
        return "<p>没有找到正文内容</p>"
