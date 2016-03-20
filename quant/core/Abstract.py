import os
import signal
from quant.core.DB import sMysql
from quant.tools.Util import sTools
from quant.settings import *


class Abstract(object):

    def __init__(self):
        self.mysql = sMysql(MYSQL_DB['host'], MYSQL_DB['user'], MYSQL_DB['password'], MYSQL_DB['dbname'])
        self.tools = sTools()

    interrupted = False

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True
