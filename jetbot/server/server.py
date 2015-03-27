#
import os
import threading
import Queue
import json
import time

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
    if command is not None:
        command = dict(up="forward",
                 left="spin_left",
                 right="spin_right",
                 down="reverse").get(command, command)

        connector = WebConnector.instance()
        if connector is not None:
            connector.put(command)


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

    timesync = TimeSync()

    def send(message):
        payload = message.__json__()
        wsock.send(json.dumps(payload))

    while True:
        try:
            timesync.activate(send)
            message = json.loads(wsock.receive())
            message["received"] = time.time()
            timesync.process(message, send)
            gevent.sleep(timesync.SYNC_INTERVAL)
        except WebSocketError:
            break


class WebConnector(object):

    INSTANCE = None


    @classmethod
    def instance(cls):
        return cls.INSTANCE


    def __init__(self, status_reporter=None):
        self._webthread = threading.Thread(target=self._run)
        self._webthread.setDaemon(True)
        self._commands = Queue.Queue()
        self._webthread.start()
        self.__class__.INSTANCE = self
        self._status_reporter = status_reporter


    def put(self, command):
        self._commands.put(command)


    @classmethod
    def _run(cls):
        server = WSGIServer(
            ("0.0.0.0", 8080),
            application=app[0],
            handler_class=WebSocketHandler)
        server.serve_forever()


    def activate(self, send):
        for _ in xrange(self._commands.qsize()):
            send(Drive(self._commands.get()))


    def process(self, _message, _send):
        pass


    @property
    def status(self):
        if self._status_reporter is not None:
            return self._status_reporter.status
        return "nostatusreporter"
