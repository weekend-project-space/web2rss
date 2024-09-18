import requests
from bs4 import BeautifulSoup
from support.config import get_item

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
    537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,\
    image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;\
    v=b3;q=0.7",
    "Connection": "keep-alive"
}

_charsets = ['GB', 'UTF', 'ISO']


def fetch(url, type='soup'):
    proxy_url = get_item('proxy_url')
    try:
        # print(f'fetch url: {url}')
        response = requests.get(url, headers=headers, timeout=10000)
        if response.status_code > 300:
            raise RuntimeError(f'status err : {response.status_code},\
                                err: {response.content}')
        print(response.apparent_encoding)
        ec = response.apparent_encoding
        if ec and len(list(filter(lambda c: c in ec, _charsets))):
            response.encoding = response.apparent_encoding
        else:
            response.encoding = 'utf-8'
        if type == 'soup':
            return BeautifulSoup(response.text, 'html.parser')
        elif type == 'text':
            return response.text
        else:
            return response
    except requests.exceptions.ConnectionError:
        print("网络连接错误，请检查网络或网址。")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
    except Exception as err:
        print(f"其他错误: {err}")
    if proxy_url not in url:
        return fetch(proxy_url+"?url="+url, type)
