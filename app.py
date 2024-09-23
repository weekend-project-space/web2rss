from flask import Flask, Response, request, make_response, render_template, \
    jsonify
# from paser.t import parser
from support.router import init_router, RouterMatch
from support.config import init_cofig
from support.gpt import gen_code, gen_code_chat
from support.dyncall import eval_rss_parser
from support.fetch import fetch
import logging
from cachetools import TTLCache
from urllib.parse import urlencode


# 创建一个具有TTL的缓存，最大存储128个结果，TTL为3600秒
cache = TTLCache(maxsize=128, ttl=3600)


class ParserConfig:
    def __init__(self,
                 request_args):
        self.request_args = request_args
        self.preview = request_args['preview'] if 'preview' in request_args\
            else False

    def req_args_str(self):
        return '?'+urlencode(self.request_args)


app = Flask(__name__)


@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    return fetch(url, 'text')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/json')
def json_example():
    data = {"message": "你好，世界"}
    return jsonify(data)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if 'messages' in data and len(data['messages']):
        return jsonify(gen_code_chat(data['messages']))
    if 'url' in data:
        d = gen_code(data['url'])
        return jsonify(d)


@app.route('/call', methods=['POST'])
def call():
    data = request.get_json()
    if data is None:
        return make_response({'error': 'error'}, 500)
    d = eval_rss_parser(data['fun'])
    return Response(d, mimetype='text/xml')


@app.route('/route/<path:key>', methods=['POST'])
def pull_route(key):
    router.pull_route(key)
    return make_response("", 201)


@app.route('/route', methods=['POST'])
def save_route():
    data = request.get_json()
    if data is None:
        return make_response({'error': 'error'}, 500)
    url = data['url']
    key = data['key']
    key = key[:-1] if key[-1] == '/' else key
    url = url[:-1] if url[-1] == '/' else url
    try:
        eval_rss_parser(data['fun'])
    except RuntimeError as e:
        return make_response({'error': str(e)}, 500)
    router.add(key, url, 'html', data['fun'])
    return make_response("", 201)


# 展示 RSS 订阅内容
@app.route('/feed', methods=['GET'])
def list_feed():
    url = request.args.get('url')

    def to_feed(r):
        if RouterMatch.can_math(r.key):
            suffix = url[len(r.url[:-1]):]
            feed = r.key[:-1] + suffix
        else:
            feed = r.key
        return {'feed': '/feed/' + feed, "url": r.url,
                "source": r.ext['source']}
    arr = list(map(to_feed, router.search_routes(url)))
    return jsonify(arr)


@app.route('/feed/<path:subpath>')
def feed(subpath):
    try:
        arg = '&'.join(f'{k}={v}' for k, v in request.args.to_dict().items())
        key = subpath + arg
        if key in cache:
            rss_xml = cache[key]
        else:
            route = router.get_route(subpath)
            rss_xml = route\
                .call_handler(subpath, ParserConfig(request.args))
            cache[key] = rss_xml
        return Response(rss_xml, mimetype='text/xml')
    except KeyError as k:
        # k.with_traceback()
        return make_response({'error': 'page nofound '+str(k)}, 404)
    except Exception as e:
        # e.with_traceback()
        return make_response({'error': str(e)}, 500)


# 启动 Flask Web 服务
if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    init_cofig()
    router = init_router()
    app.run(host='0.0.0.0', port=3390)
