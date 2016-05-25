# -*- coding: utf-8 -*-
import sys
import time
import datetime
import logging
import hashlib
from quant.core.Spider import *


class IndexSpider(SpiderEngine):
    '''
    更新指数
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def run(self):
        self.tools.setup_logging(sys.argv[1], True, True)

        logging.debug('Start Daily 000001 & 399006 Data=====Days:%s ' % sys.argv[2])

        nindex = ['000001', '399006']
        dateline = sys.argv[2]
        d = datetime.datetime.strptime(dateline, "%Y%m%d")
        jidu = int(self.tools.d_date('%m', time.mktime(d.timetuple())))
        jidu = int((jidu+3-1)/3)
        for i in range(0, len(nindex)):
            url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s/type/S.phtml?year=%s&jidu=%s" % (nindex[i], self.tools.d_date('%Y', time.mktime(d.timetuple())), int(jidu))
            self._format_index_data(nindex[i], url, dateline)

    def get_history_data(self):
        nindex = ['000001', '399006']
        for i in range(2010, 2017):
            for j in range(1, 5):
                url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s/type/S.phtml?year=%s&jidu=%s" % (nindex[0], i, j)
                print url
                self._format_index_data(nindex[i], url, 0)

    def _format_index_data(self, index, url, clear=''):
        logging.debug('Start Daily 000001 & 399006 Url=====:%s ' % url)
        _data = self.sGet(url)
        _data = self.sMatch('<table id="FundHoldSharesTable">', '<\/table>', _data, 0)

        _res = self.sMatch('<tr(.*?)>', '<\/tr>', _data[0], 0)

        for i in range(2, len(_res)):
            _tmp = self.sMatch('<div align="center">', '<\/div>', _res[i][1], 0)

            _d = self.tools.strip_tags(_tmp[0])
            _d = _d.replace("\t", "")
            _d = _d.replace("\n", "")
            _d = _d.replace("\r", "")
            _d = _d.replace("-", "")
            if clear and _d != clear:
                continue

            word = "%s%s" % (index, _d)
            _hash = hashlib.md5(word).hexdigest()
            indata = {
                'dateline': _d,
                'zs_code': index,
                'hash': _hash,
                'open': _tmp[1],
                'high': _tmp[2],
                'close': _tmp[3],
                'low': _tmp[4],
                'volumes': _tmp[5],
                'volumes_money': _tmp[6]
            }
            _has = self.mysql.fetch_one("select * from  s_index where hash='%s'" % _hash)
            _where = "hash='%s'" % _hash
            if _has is not None:
                self.mysql.dbUpdate('s_index', indata, _where)
            else:
                self.mysql.dbInsert('s_index', indata)
            print indata
