# -*- coding: utf-8 -*-
import hashlib
from quant.core.Stats import *


class LhbCount(StatsEngine):

    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        dateline = self.args[2]
        x = self.mysql.getRecord("SELECT * FROM  `s_lhb_days_detail` WHERE  `dateline` =%s" % dateline)
        _data = {}
        xhash = []
        for k in range(0, len(x)):
            if x[k]['yyb_id'] == 0 or x[k]['yyb_id'] == 8888:
                continue

            if x[k]['yyb_id'] not in _data:
                _data[x[k]['yyb_id']] = {'B': 0, 'S': 0}

            word = "%s%s%s" % (x[k]['s_code'], x[k]['B_volume'], x[k]['S_volume'])
            _md5 = hashlib.md5(word).hexdigest()
            if _md5 in xhash:
                continue

            xhash.append(_md5)
            _data[x[k]['yyb_id']]['B'] += x[k]['B_volume']
            _data[x[k]['yyb_id']]['S'] += x[k]['S_volume']

        if len(_data) > 0:
            for k, v in _data.items():
                if v['B'] == 0 and v['S'] == 0:
                    continue
                indata = {
                    'yyb_id': k,
                    'B': v['B'],
                    'S': v['S'],
                    'dateline': dateline
                }
                self.mysql.dbInsert('s_lhb_daily', indata)
