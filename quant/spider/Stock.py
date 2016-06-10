# -*- coding: utf-8 -*-
import sys
import logging
import json
from decimal import *
from quant.core.Spider import *


class StockSpider(SpiderEngine):
    '''
    更新指数
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def run(self):
        self.tools.setup_logging(sys.argv[1], True, True)

        #self.get_xueqiu_base(1)
        #sys.exit()

        logging.debug('Start Base Stock=====Days:%s ' % sys.argv[2])
        day_list = self.mysql.getRecord("SELECT * FROM  `s_stock_list` WHERE  `run_market` =0 OR all_market =0")
        for i in range(0, len(day_list)):
            self.get_xueqiu_base(day_list[i])

    def get_level_2():
        #十档行情
        #https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=300190
        pass

    def get_xueqiu_base(self, data):

        #s_code = 'SH600180'
        #print data
        s_code = data['s_code'].upper()
        self.curl_get('https://xueqiu.com/8205215793')
        url = "https://xueqiu.com/v4/stock/quote.json?code=%s&_=1423121365509" % s_code
        #url = "https://www.baidu.com"
        _data = self.curl_get(url)
        re = json.loads(_data)
        #流通
        a = int(Decimal(re[s_code]['float_shares']) * data['close'])
        #总股
        b = int(Decimal(re[s_code]['totalShares']) * data['close'])
        self.mysql.dbQuery("update s_stock_list set run_market=%s,all_market=%s where id=%s" % (a, b, data['id']))
