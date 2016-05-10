#! -*- coding:utf-8 -*-
'''
Mercury
Quantz
CAL

'''
MYSQL_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234asdf',
    'dbname': 'stock'
}
JOB_LOGS_DIRECTORY = '/tmp/quant'
DAILY_STRONG_LOG = '/htdocs/quant/data/strong_%s.blk'
#分钟数据
MIN_DATA_LOG = '/htdocs/quant/data/min'

#blacklist
STOCK_BLANK_LIST = []

#cache
MEMCACHE_HOST = ['127.0.0.1:11211']

ES_CONFIG = {
    'host': 'localhost',
    'port': '9200',
}
