# -*- coding: utf-8 -*-
from quant.core.Stats import *


class MaCount(StatsEngine):
    #每日收盘价在均线之上
    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        indate = self.args[2]
        _data = self.mysql.getRecord("select s_code,dateline,ma5,ma10,ma20,ma30,ma60 from s_stock_average where dateline = %s" % indate)
        _st_data = self.mysql.getRecord("select s_code,close from s_stock_trade where dateline= %s" % indate)
        b = {}
        for row in _st_data:
            b[row['s_code']] = row['close']

        for row in _data:
            _d_c = b[row['s_code']]
            sql = []
            if _d_c >= row['ma5']:
                sql.append('on_ma5=on_ma5+1')
            if _d_c >= row['ma10']:
                sql.append('on_ma10=on_ma10+1')
            if _d_c >= row['ma20']:
                sql.append('on_ma20=on_ma20+1')
            if _d_c >= row['ma30']:
                sql.append('on_ma30=on_ma30+1')
            if _d_c >= row['ma60']:
                sql.append('on_ma60=on_ma60+1')
            if len(sql) > 0:
                self.mysql.dbQuery("update s_daily_report set %s where dateline=%s" % (','.join(sql), indate))
        print "MA Done.."
