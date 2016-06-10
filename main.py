# -*- coding: utf-8 -*-
import sys
#from quant.core.StrategyEngine import *
#from quant.core.BackTestingEngine import *
from quant.selecter.Wpkiller import *
from quant.selecter.DailyStrong import *
from quant.selecter.Dma import *
from quant.selecter.DailyTrend import *
from quant.selecter.RealVolumeRate import *

#from elasticsearch import Elasticse
#es = Elasticsearch(host="localhost", port="9200")
from quant.tools.Util import sTools


def main_test():
    setting = {}
    setting['start'] = 20150101
    setting['end'] = 20151222
    setting['benchmark'] = 'HS300'
    #setting['universe'] = ['sz300019', 'sh600836']
    setting['universe'] = ['CYB', 'ZXB']
    # 起始资金
    setting['capital_base'] = 10000000
    # 策略类型，'d'表示日间策略使用日线回测，'m'表示日内策略使用分钟线回测
    setting['freq'] = 'd'

    b = DmaSelecter(setting)
    b.run()


def wpKiller(end):

    setting = {}
    setting['start'] = 20160603
    setting['end'] = end
    setting['limit'] = 3
    a = WpKillerSelecter(setting)
    a.run()


def dailyStrong(end):
    setting = {}
    setting['start'] = '20160530'
    setting['end'] = end
    setting['limit'] = 3
    b = DailyStrongSelecter(setting)
    b.run()


def RealVolumeRate(end):
    setting = {}
    #setting['start'] = '20160530'
    setting['end'] = end
    setting['limit'] = 3
    b = RealVolumeRateSelecter(setting)
    b.run()


def daily(end):
    setting = {}
    setting['start'] = 20160530
    setting['end'] = end
    setting['limit'] = 3

    #a = WpKillerSelecter(setting).run()
    #a = DailyStrongSelecter(setting).run()
    d = RealVolumeRateSelecter(setting).run()

    tofile = '/htdocs/quant/data/%s.blk' % sTools.d_date('%Y%m%d')
    fp = open(tofile, 'a+')
    #d = a + b
    #d = list(set(d))
    for i in range(0, len(d)):
        loc = 0
        if d[i][0:2] == 'sh':
            loc = 1
        zxb = str(loc) + str(d[i][2:10]) + "\r\n"
        fp.write(zxb)


def dma(end):
    setting = {}
    setting['start'] = 20160301
    setting['end'] = end
    #setting['universe'] = ['sz300208']
    #setting['universe'] = ['CYB']
    '''
    query_body = {
        'query': {
            'bool': {
                'must': [
                    {"match": {"tagss": "迪斯尼"}},
                    {"range": {"run_market": {"gte": 40, "lt": 67}}}
                ],
                'should': [],
                'must_not': []
            },
            #"filtered": {"filter": {}}
        }
    }
    res = es.search(index="stock8", doc_type='info', body=query_body)
    #results = json.dumps(results, indent=4)
    print res
    print res['hits']['total']
    for hit in res['hits']['hits']:
        print hit['_source']['name']
        print "=========="
    sys.exit()
    '''

    setting['limit'] = 180
    setting['is_open_chuquan'] = True
    b = DmaSelecter(setting)
    b.run()


def main_trend():
    '''
    'sz000026',
    sz000691 创新高
    '''
    setting = {}
    setting['start'] = 20150101
    setting['end'] = 20151225
    setting['universe'] = ['sz000691']
    setting['limit'] = 4
    b = DailyTrendSelecter('pxhkiller', setting)
    b.run()

if __name__ == '__main__':
    #初始化策略类
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('RealVolumeRate', help=u'实时成交与流通盘比率,观察当日热点')
    parser.set_defaults(func=sys.argv)
    parser.add_argument('dailyStrong', help=u'N天涨幅超过25%')
    parser.add_argument('dma', help=u'白线在黄线之上,长期趋势,量度决定速度')
    parser.add_argument('wpKiller', help=u'跳开，冲高回落')
    args = parser.parse_args()
    args.func(args)
    '''
    sTools = sTools()
    print sys.argv
    if len(sys.argv) > 2:
        function = eval(sys.argv[1])
        function(sys.argv[2])
