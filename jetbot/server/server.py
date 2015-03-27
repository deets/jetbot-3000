#
import os
import threading
import Queue
import json
import time
import logging

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

from .bottle import (
    abort,
    route,
    template,
    static_file,
    request,
    TEMPLATE_PATH,
    app,
    )

from ..protocol import Drive, TimeSync
from ..base import message_valid

logger = logging.getLogger(__name__)


TEMPLATE_PATH.insert(0, os.path.join(
    os.path.dirname(__file__),
    "views",
    )
)

@route('/')
def index():
    return template('index')


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(
        filename,
        root=os.path.join(
            os.path.dirname(__file__),
            "static",
            )
        )


@route('/track', method="POST")
def track():
    data = request.json
    command = data.get("command")
    timestamp = data.get("timestamp")
    if command is not None and timestamp is not None:
        command = dict(up="forward",
                 left="spin_left",
                 right="spin_right",
                 down="reverse").get(command, command)

        connector = WebConnector.instance()
        if connector is not None:
            connector.put(
                dict(
                    command=command,
                    timestamp=timestamp,
                )
            )


@route('/status')
def status():
    connector = WebConnector.instance()
    if connector is not None:
        status = connector.status
    else:
        status = "nowebconnector"
    return dict(status=status)


@route('/websocket')
def websocket():
    wsock = request.environ.get('wsgi.websocket')

    if not wsock:
        abort(400, 'Expected WebSocket request.')

    logger.info("timesync connected")

    timesync = WebConnector.instance().timesync

    def send(message):
        payload = message.__json__()
        wsock.send(json.dumps(payload))

    while True:
        try:
            timesync.activate(send)
            input_message = wsock.receive()
            if input_message is not None:
                message = json.loads(input_message)
                message["received"] = time.time()
                timesync.process(message, send)
            gevent.sleep(timesync.SYNC_INTERVAL / 10.0)
        except WebSocketError:
            break
        except:
            logger.exception("Exception during websocket handling")


class WebConnector(object):

    INSTANCE = None


    @classmethod
    def instance(cls):
        return cls.INSTANCE


    def __init__(self, status_reporter=None, threshold=0.5):
        self._threshold = threshold
        self._webthread = threading.Thread(target=self._run)
        self._webthread.setDaemon(True)
        self._commands = Queue.Queue()
        self._webthread.start()
        self.__class__.INSTANCE = self
        self._status_reporter = status_reporter
        self.timesync = TimeSync()


    def put(self, command):
        self._commands.put(
            dict(
                command=command["command"],
                timestamp=command["timestamp"],
                received=time.time(),
                )
            )


    @classmethod
    def _run(cls):
        server = WSGIServer(
            ("0.0.0.0", 8080),
            application=app[0],
            handler_class=WebSocketHandler)
        server.serve_forever()


    def activate(self, send):
        offset = self.timesync.offset
        for _ in xrange(self._commands.qsize()):
            command = self._commands.get()

            if offset is not None and message_valid(
                    threshold=self._threshold,
                    received=command["received"],
                    remote_timestamp=command["timestamp"],
                    remote_offset=offset):
                send(Drive(command["command"]))
            else:
                logger.debug("throwing away message %r with offset %f", command, offset)


    def process(self, _message, _send):
        pass


    @property
    def status(self):
        if self._status_reporter is not None:
            return self._status_reporter.status
        return "nostatusreporter"
