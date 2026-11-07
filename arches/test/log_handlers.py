import logging
import sys


class CurrentStderrHandler(logging.StreamHandler):
    """Writes to whatever sys.stderr is at emit time, so unittest's
    --buffer (which swaps sys.stderr per test) captures log output."""

    def __init__(self):
        logging.Handler.__init__(self)

    @property
    def stream(self):
        return sys.stderr

    @stream.setter
    def stream(self, value):
        pass
