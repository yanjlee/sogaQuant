# -*- coding: utf-8 -*-
import sys
import time
from quant.spider.MinData import *
#from quant.spider.Handicap import *
#from quant.core.DB import sMysql

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


def get_min_data(abc):
    #20分钟一次获取各股的长跌幅
    s = MinDataSpider()
    s.run()


def while_change():
    #5分钟一次获取各股的涨跌幅
    RealTimeChange(sys.argv).run()


def demo():
    SecondDrawStats(sys.argv).run()


def pankou_replay():
    #盘后 对挂单超过2KW的单子进行监控
    Pankou().replay()


def pankou_realtime():
    #实时盘口显示,超1KW
    Pankou().realtime()


def pankou_open():
    #每日open last_close 写入
    Pankou().daily_open()


def pankou_save():
    '''
    获取实时5档买卖盘口
    python realtime.py get_five_sb 页数
    '''
    while 1:
        Pankou().save()


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
    function()
    end = time.time()
    print end-start
