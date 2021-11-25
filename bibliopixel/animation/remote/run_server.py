from ... util import log
import logging
import sys
import xmod

MESSAGE = """\
Remote UI Server available at: {1}
Local: http://localhost:{0}"""

EXTERNAL_ACCESS_MESSAGE = MESSAGE + """
External: http://<system_ip>:{0}"""


@xmod
def run_server(external_access, port, q_send, q_recv):
    from . server import RemoteServer, app
    import werkzeug.serving

    if '--verbose' not in sys.argv:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    server = RemoteServer(q_recv, q_send)
    if external_access:
        host_ip = '0.0.0.0'
        msg = EXTERNAL_ACCESS_MESSAGE
    else:
        host_ip = 'localhost'
        msg = MESSAGE

    log.info(msg.format(port, host_ip))

    try:
        werkzeug.serving.run_simple(host_ip, port, app, threaded=False)
    except (KeyboardInterrupt, SystemExit):
        return
