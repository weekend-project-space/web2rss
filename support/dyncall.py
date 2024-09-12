import importlib
from support.fetch import fetch
import PyRSS2Gen
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def call(module_name, url, config):
    # 动态加载模块
    module = importlib.import_module(module_name)
    # 使用模块中的函数或变量
    return module.parser(url, config)


def eval_rss_parser(code):
    # print(code)
    exec(code)
    r = locals()['parser']()
    return r.to_xml(encoding='utf-8')
