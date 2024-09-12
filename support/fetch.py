import requests
from bs4 import BeautifulSoup
from support.config import get_item

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}


def fetch(url, type='soup'):
    proxy_url = get_item('proxy_url')
    try:
        # print(f'fetch url: {url}')
        response = requests.get(url, headers=headers, timeout=10000)
        if response.status_code > 300:
            raise RuntimeError(f'status err : {response.status_code}')
        response.encoding = response.apparent_encoding
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
