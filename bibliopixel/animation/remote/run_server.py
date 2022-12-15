from . import server
from ... util import log
import logging
import sys
import xmod

MESSAGE = """\
Remote UI Server available at: {1}
Local: http://localhost:{0}"""

EXTERNAL_ACCESS_MESSAGE = MESSAGE + """
External: http://<system_ip>:{0}"""


def run_server(external_access, port, q_send, q_recv):
    if '--verbose' not in sys.argv:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    if external_access:
        host = '0.0.0.0'
        msg = EXTERNAL_ACCESS_MESSAGE
    else:
        host = 'localhost'
        msg = MESSAGE

    log.info(msg.format(port, host))

    app = server.server(q_send, q_recv)
    import werkzeug.serving
    try:
        werkzeug.serving.run_simple(host, port, app, threaded=False)
    except (KeyboardInterrupt, SystemExit):
        return
