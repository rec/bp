from ... util import log
import bibliopixel, flask, os, queue
import logging
import sys

MESSAGE = """\
Remote UI Server available at: {1}
Local: http://localhost:{0}"""

EXTERNAL_ACCESS_MESSAGE = MESSAGE + """
External: http://<system_ip>:{0}"""


ROOT_DIR = os.path.dirname(os.path.dirname(bibliopixel.__file__))
STATIC_DIR = os.path.join(ROOT_DIR, 'ui', 'web_remote')
assert os.path.exists(STATIC_DIR)


def shutdown():
    log.warning('Shutting down UI server.')
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return False
    func()
    return True


def server(q_send, q_recv):
    app = flask.Flask('BP Remote', static_folder=STATIC_DIR)

    @app.route('/')
    def index():
        log.debug('index.html')
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def static_files(path):
        log.debug('static_files: %s', path)
        return app.send_static_file(path)

    @app.route('/run_animation/<string:animation>')
    def run_animation(animation):
        return api('run_animation', data=animation)

    @app.route('/stop')
    def stop_animation(self):
        return api('stop_animation')

    @app.route('/api/<string:request>')
    @app.route('/api/<string:request>/<data>')
    def api(request, data=None):
        log.debug('api: %s, %s', request, data)
        q_send.put({
            'req': request.lower(),
            'data': data,
            'sender': 'RemoteServer',
        })

        try:
            status, data = q_recv.get(timeout=5)
            msg = 'OK'
        except queue.Empty:
            status, data = False, None
            msg = 'Timeout waiting for response.'

        return flask.jsonify({'status': status, 'msg': 'msg', 'data': data})

    return app
