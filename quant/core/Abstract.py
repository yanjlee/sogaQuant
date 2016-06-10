#! -*- coding:utf-8 -*-
import os
import json
import signal
import time
import logging

from quant.core.DB import sMysql
from quant.tools.Util import sTools


class Abstract(object):
    benchmart_start = 0
    benchmart_end = 0

    def __init__(self):
        self.tools = sTools()
        self.benchmart_start = time.clock()
        self.__read_config()
        mysql_db = self.config['mysql']['stock']
        self.mysql = sMysql(mysql_db['host'], mysql_db['user'], mysql_db['password'], mysql_db['dbname'])

    interrupted = False

    def __del__(self):
        self.benchmart_end = time.clock()
        time_str = "Runtime: %f s" % (self.benchmart_end - self.benchmart_start)
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        host = self
        pid = os.getpid()
        header = '{0} {1}[{2}]:\n{3}\n'
        print header.format(date, host, pid, time_str)

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True

    def __read_config(self):
        """读取 config"""
        self.config_path = os.path.dirname(__file__) + '/../../config.json'
        self.config = self.file2dict(self.config_path)
        #self.global_config = self.file2dict(self.global_config_path)
        #self.config.update(self.global_config)

    def file2dict(self, path):
        with open(path) as f:
            return json.load(f)

    def run_php(self, path):
        cmd = 'php /htdocs/quant/soga/mv/index.php %s' % path
        os.system(cmd)
