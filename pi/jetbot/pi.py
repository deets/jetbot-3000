
def pi_protocol_test():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()

    setup_logging(opts)

    uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect(uri)
    time_sync = TimeSync()

    logger.info("Connecting to '%s'", uri)

    send = partial(send_message, socket)

    while True:
        packet = socket.recv()
        now = time.time()
        message = json.loads(packet)
        message["received"] = now
        logger.debug(json.dumps(message))
        time_sync.process(message, send)
