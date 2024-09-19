from support.fetch import fetch
from support.config import get_item
from support.dyncall import call
from support.url2mc import url2maincontent
import os
import logging

logger = logging.getLogger(__name__)


class Route:
    def __init__(self, key, url, meta='', type='html'):
        self.key = key
        self.url = url
        self.meta = meta or '{}={},{}'.format(key, url, type)
        self.type = type
        self.ext = {"source": "local"}

    def call_handler(self, subpath, config):
        if RouterMatch.can_math(self.key):
            suffix = subpath[len(self.key[:-1]):]
            url = self.url[:-1] + suffix
        if self.type == "proxy":
            return fetch(url, '').text
        else:
            moudle = 'repo.'+_get_module_path(self.key)
            rss = call(moudle, url, config)
            if config.preview:
                self._preview(rss)
            return rss.to_xml(encoding='utf-8')

    def put_ext(self, key, v):
        self.ext[key] = v
        return self

    def _preview(self, rss):
        items = []
        for item in rss.items:
            items.append(item)
            if item.title == item.description:
                try:
                    d = url2maincontent(item.link)
                    item.description = d
                except RuntimeError as e:
                    logger.warning(f"fetch item error: {e}")
        rss.items = items


class Router:
    def __init__(self, routes, router_file_path='router.txt'):
        self.routes = routes
        self._remote_url = get_item('remote_url')
        self._local_repo_path = get_item('local_repo_path')
        self._router_file_path = router_file_path
        logger.info(f"init {router_file_path} routes: {routes.keys()}")

    def _call(self, fn):
        return fn(self.routes)

    def search(self, filter_fn):
        return list(filter(filter_fn, self.routes.values()))

    def get_route(self, key):
        if key in self.routes.keys():
            return self.routes[key]
        else:
            keys = list(filter(lambda k:  RouterMatch.match(key, k),
                               self.routes.keys()))
            if len(keys) == 1:
                return self.routes[keys[0]]
            else:
                KeyError('key not found:' + key)

    def search_routes(self, url):
        def has_url(r):
            return r.url == url or r.key in url or\
                RouterMatch.match(url, r.url) or\
                RouterMatch.match(url, r.key)
        routes = self.search(has_url)
        if len(routes) > 0:
            return routes
        routes = _get_remote_router_no_err().search(has_url)
        if len(routes) > 0:
            return list(map(lambda r:  r.put_ext('source', 'remote'), routes))
        res_text = fetch(url, 'text')
        if _is_rss_or_atom(res_text):
            key = url.split('://')[1]
            self.add(key, url, 'proxy')
            routes = self.search(has_url)
            if len(routes) > 0:
                return routes
        return []

    def add(self, key, url, type, parserStr=None):
        route = Route(key, url, None, type)
        if parserStr is not None and parserStr.strip() != "":
            _write_parser_file(self._local_repo_path, key, parserStr)
        _append_router_file(self._router_file_path, route.meta)
        self.routes[key] = route

    def pull_route(self, key):
        _pullRoute(self._remote_url, self._local_repo_path,
                   self._router_file_path, key)
        self.refresh()

    def refresh(self):
        self.routes = _init_routes(self._router_file_path)


def init_router(router_file_path="router.txt"):
    return Router(_init_routes(router_file_path), router_file_path)


def _init_routes(router_file_path):
    with open(router_file_path, 'r') as file:
        return _bulid_routes(file)


class RouterMatch:

    def can_math(key):
        return key[-1:] == '*'

    def match(url, key):
        if key[-1:] == '*':
            return key[:-1] in url
        else:
            False


def _reverse_domain(domain):
    # 分割域名为各部分
    parts = domain.split('.')
    # 反向排序各部分
    reversed_parts = parts[::-1]
    # 合并成新的域名
    reversed_domain = '.'.join(reversed_parts)
    return reversed_domain


def _get_module_path(key):
    # key = subpath
    if RouterMatch.can_math(key):
        key = key[:-1]+'dyncall'
    paths = key.split('/')
    paths[0] = _reverse_domain(paths[0])
    return ".".join(paths)


def _bulid_routes(lines):
    routes = {}
    for line in lines:
        key, value = line.strip().split('=', 1)
        if ',' in value:
            vs = value.split(',')
            routes[key] = Route(key, vs[0], line, vs[1])
        else:
            routes[key] = Route(key, value, line)
    return routes


def _get_remote_router_no_err():
    try:
        return _get_remote_router()
    except Exception:
        return Router({}, 'remote')


_remote_router_cache = None


def _get_remote_router():
    global _remote_router_cache
    if _remote_router_cache is None:
        url = get_item('remote_url')+'/router.txt'
        # print(url)
        remote_routes_file = fetch(url, 'text')
        # print(remote_routes_file)
        _remote_router_cache = Router(
            _bulid_routes(remote_routes_file.split('\n')), 'remote')
    return _remote_router_cache


def _pullRoute(remote_url, local_repo_path, local_router_path, key):
    repo_url = "{}/repo/{}.py".format(remote_url, _get_module_path(key).
                                      replace('.', '/'))
    parser_py_str = fetch(repo_url, 'text')
    _write_parser_file(local_repo_path, key, parser_py_str)
    line = _get_remote_router().search(lambda r: r.key == key)[0].meta
    # print(local_router_path)
    _append_router_file(local_router_path, line)


def _write_parser_file(local_repo_path, key, parser_py):
    local_parser_path = "{}/repo/{}.py".format(local_repo_path,
                                               _get_module_path(key).
                                               replace('.', '/'))
    local_parser_path = local_parser_path[2:] if local_parser_path[:2] == './'\
        else local_parser_path
    # print(local_parser_path)
    __write_file(local_parser_path, 'w', parser_py)


def _append_router_file(local_router_path, line):
    # 要追加的内容
    __write_file(local_router_path, 'a', '\n'+line)


def __write_file(file_path, mode, content):
    # 获取文件所在的目录路径
    dir_path = os.path.dirname(file_path)
    if dir_path != '':
        # 如果目录不存在，就创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    # 写入文件
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(content)


def _is_rss_or_atom(content):
    return content is not None and ('<rss' in content or '<feed' in content)
