# -*- coding: utf-8 -*-
import sys
import time
import memcache
from quant.spider.MinData import *
from quant.spider.Handicap import *
from quant.core.DB import sMysql

from quant.stats.RealTimeChange import *
from quant.stats.SecondDraw import *
from quant.stats.Pankou import *


def __read_config():
    """读取 config"""
    config_path = 'config.json'
    config = file2dict(config_path)
    return config


def file2dict(path):
    with open(path) as f:
        return json.load(f)


def get_five_sb(abc):
    '''
    获取实时5档买卖盘口
    python realtime.py get_five_sb 页数
    '''
    config = __read_config()
    mysql_db = config['mysql']['stock']
    mysql = sMysql(mysql_db['host'], mysql_db['user'], mysql_db['password'], mysql_db['dbname'])

    mcache = memcache.Client(['127.0.0.1:11211'])
    #print mcache.set('say','hello,memcache') #display - True
    while 1:
        HandicapSpider().run(mysql, mcache)
        #sys.exit()
        #time.sleep(1)


def get_min_data(abc):
    #20分钟一次获取各股的长跌幅
    s = MinDataSpider()
    s.run()


def while_change(abc):
    #5分钟一次获取各股的涨跌幅
    RealTimeChange(sys.argv).run()


def demo(abc):
    SecondDrawStats(sys.argv).run()


def pankou(abc):
    #对挂单超过2KW的单子进行监控
    Pankou(sys.argv).run()


def realtime_pankou(self):
    #实时盘口显示,超1KW
    Pankou(sys.argv).realtime()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--nimbus-host', default='127.0.0.1')
    parser.add_argument('--nimbus-port', type=int, default=6627)
    #args = parser.parse_args()
    #Job(args).run()
    #sys.exit()
    start = time.time()
    function = eval(sys.argv[1])
    function(sys.argv[2])
    end = time.time()
    print end-start
