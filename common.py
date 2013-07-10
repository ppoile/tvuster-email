import logging.handlers


def setup_logging(verbose=True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        "tmp/tvuster-email.log", maxBytes=100000, backupCount=2)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(name)-30s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    if verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-30s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger = logging.getLogger("requests")
    logger.setLevel(logging.WARNING)
