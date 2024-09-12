from support.fetch import fetch
from support.config import get_item
from support.dyncall import call
import os


class Route:
    def __init__(self, key, url, meta='', type='html'):
        self.key = key
        self.url = url
        self.meta = meta or '{}={},{}'.format(key, url, type)
        self.type = type
        self.ext = {"source": "local"}

    def call_handler(self, config):
        if self.type == "proxy":
            return fetch(self.url, '').text
        else:
            moudle = 'repo.'+_get_module_path(self.key)
            return call(moudle, self.url, config).to_xml(encoding='utf-8')

    def put_ext(self, key, v):
        self.ext[key] = v
        return self


class Router:
    def __init__(self, routes, router_file_path='router.txt'):
        self.routes = routes
        self._remote_url = get_item('remote_url')
        self._local_repo_path = get_item('local_repo_path')
        self._router_file_path = router_file_path
        print(f"init {router_file_path} routes: {routes}")

    def _call(self, fn):
        return fn(self.routes)

    def search(self, filter_fn):
        return list(filter(filter_fn, self.routes.values()))

    def get_route(self, key):
        route = self.routes[key]
        if route:
            return route
        else:
            KeyError('key not found:' + key)

    def search_routes(self, url):
        def has_url(r):
            return r.url == url or r.key in url
        routes = self.search(has_url)
        if len(routes) > 0:
            return routes
        res_text = fetch(url, 'text')
        if _is_rss_or_atom(res_text):
            key = url.split('://')[1]
            self.add(key, url, 'proxy')
            routes = self.search(has_url)
            if len(routes) > 0:
                return routes
        routes = _get_remote_router_no_err().search(has_url)
        return list(map(lambda r:  r.put_ext('source', 'remote'), routes))

    def add(self, key, url, type, parserStr=None):
        route = Route(key, url, None, type)
        if parserStr is not None and parserStr.strip() != "":
            _write_parser_file(self._local_repo_path, key, parserStr)
        _append_router_file(self._local_repo_path+'/router.txt', route.meta)
        self.routes[key] = route

    def pull_route(self, key):
        _pullRoute(self._remote_url, self._local_repo_path, key)
        self.refresh()

    def refresh(self):
        self.routes = __init_routes(self._router_file_path)


def init_router(router_file_path="router.txt"):
    return Router(__init_routes(router_file_path), router_file_path)


def __init_routes(router_file_path):
    with open(router_file_path, 'r') as file:
        return _bulid_routes(file)


def _reverse_domain(domain):
    # 分割域名为各部分
    parts = domain.split('.')
    # 反向排序各部分
    reversed_parts = parts[::-1]
    # 合并成新的域名
    reversed_domain = '.'.join(reversed_parts)
    return reversed_domain


def _get_module_path(subpath):
    paths = subpath.split('/')
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


def _get_remote_router():
    remote_routes_file = fetch(get_item('remote_url')+'/router.txt', 'text')
    return Router(_bulid_routes(remote_routes_file), 'remote')


def _pullRoute(remote_url, local_repo_path, key):
    repo_url = "{}/repo/{}.py".format(remote_url, _get_module_path(key).
                                      replace('.', '/'))
    parser_py_str = fetch(repo_url, 'text')
    _write_parser_file(local_repo_path, key, parser_py_str)
    line = _get_remote_router().search(lambda r: r.key == key)[0].meta
    local_router_path = local_repo_path + 'router.txt'
    _append_router_file(local_router_path, line)


def _write_parser_file(local_repo_path, key, parser_py):
    local_parser_path = "{}/repo/{}.py".format(local_repo_path,
                                               _get_module_path(key).
                                               replace('.', '/'))
    local_parser_path = local_parser_path[2:] if local_parser_path[:2] == './'\
        else local_parser_path
    print(local_parser_path)
    __write_file(local_parser_path, 'w', parser_py)


def _append_router_file(local_router_path, line):
    # 要追加的内容
    __write_file(local_router_path, 'a', '\n'+line)


def __write_file(file_path, mode, content):
    # 获取文件所在的目录路径
    dir_path = os.path.dirname(file_path)
    # 如果目录不存在，就创建目录
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # 写入文件
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(content)


def _is_rss_or_atom(content):
    return ('<rss' in content or '<feed' in content)
