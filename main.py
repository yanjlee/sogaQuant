# -*- coding: utf-8 -*-
import sys
#from quant.core.StrategyEngine import *
#from quant.core.BackTestingEngine import *
from quant.selecter.Wpkiller import *
from quant.selecter.DailyStrong import *
from quant.selecter.Dma import *
from quant.selecter.DailyTrend import *

#from quant.core.Spider import SpiderEngine
#from elasticsearch import Elasticse
#es = Elasticsearch(host="localhost", port="9200")


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

    b = DmaSelecter('pxhkiller', setting)
    b.run()


def main_killer():

    setting = {}
    setting['start'] = '20160114'
    setting['end'] = '20160115'
    setting['limit'] = 3
    a = WpKillerSelecter('wpkiller', setting)
    a.run()


def main_dailyStrong(end):
    setting = {}
    setting['start'] = '20160510'
    setting['end'] = end
    setting['limit'] = 3
    b = DailyStrongSelecter('phkiller', setting)
    b.run()


def main_dma(end):
    setting = {}
    setting['start'] = 20150301
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
    b = DmaSelecter('pxhkiller', setting)
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
    #main_dailyStrong(sys.argv[1])
    main_dailyStrong(sys.argv[1])
    #main_dma(sys.argv[1])
