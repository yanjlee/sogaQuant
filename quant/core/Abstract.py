#! -*- coding:utf-8 -*-
import os
import json
import signal
from quant.core.DB import sMysql
from quant.tools.Util import sTools


class Abstract(object):

    def __init__(self):
        self.tools = sTools()
        self.__read_config()
        mysql_db = self.config['mysql']['stock']
        self.mysql = sMysql(mysql_db['host'], mysql_db['user'], mysql_db['password'], mysql_db['dbname'])

    interrupted = False

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
