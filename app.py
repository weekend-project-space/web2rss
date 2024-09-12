from flask import Flask, Response, request, make_response, render_template, \
    jsonify
# from paser.t import parser
from support.router import init_router
from support.config import init_cofig
from support.gpt import gen_code, gen_code_chat
from support.dyncall import eval_rss_parser


class ParserConfig:
    def __init__(self,
                 request_args):
        self.request_args = request_args


app = Flask(__name__)


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
    router.add(key, url, 'html', data['fun'])
    return make_response("", 201)


# 展示 RSS 订阅内容
@app.route('/feed', methods=['GET'])
def list_feed():
    url = request.args.get('url')

    def to_feed(r):
        return {'feed': '/feed/' + r.key, "url": r.url,
                "source": r.ext['source']}
    arr = list(map(to_feed, router.search_routes(url)))
    return jsonify(arr)


@app.route('/feed/<path:subpath>')
def feed(subpath):
    try:
        route = router.get_route(subpath)
        rss_xml = route\
            .call_handler(ParserConfig(request.args))
        return Response(rss_xml, mimetype='text/xml')
    except KeyError:
        return make_response({'error': 'page nofound'}, 404)
    except Exception as e:
        return make_response({'error': str(e)}, 500)


# 启动 Flask Web 服务
if __name__ == '__main__':
    init_cofig()
    router = init_router()
    app.run(host='0.0.0.0', port=3390)
