# -*- coding: utf-8 -*-
from decimal import Decimal
from quant.core.Stats import *


class Summary(StatsEngine):

    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        indate = self.args[2]
        data = self.mysql.getRecord("select high,close,last_close,chg,s_code from s_stock_trade where dateline=%s" % indate)
        _data_lhb = self.mysql.getRecord("select s_code,yyb_id,B_volume,S_volume from s_lhb_days_detail where dateline=%s" % indate)
        res = {
            'dateline': indate,
            'lhb_max': 0,
            'lhb_in': 0,
            'lhb_out': 0,
            'zt_top': 0,
            'zt_last': 0,
            'zt_open': 0,
            'sz_max': 0,
            'sz_up': 0,
            'sz_down': 0
            }
        _tmp = {}
        _tmp_yyb = {}
        for row in _data_lhb:
            #一个票中营业部买入又卖出
            if len(_tmp) > 0 and row['s_code'] in _tmp.keys() and row['yyb_id'] in _tmp[row['s_code']]:
                continue
            if row['yyb_id'] not in _tmp_yyb.keys():
                _tmp_yyb[row['yyb_id']] = []

            _cn = row['B_volume'] - row['S_volume']
            _tmp_yyb[row['yyb_id']].append(_cn)

            if row['s_code'] not in _tmp.keys():
                _tmp[row['s_code']] = []

            _tmp[row['s_code']].append(row['yyb_id'])

        if len(_tmp_yyb) > 0:
            for yyb_id, value in _tmp_yyb.items():
                x = sum(value)
                res['lhb_max'] += 1
                if x > 0:
                    res['lhb_in'] += 1
                else:
                    res['lhb_out'] += 1

        for row in data:
            if row['high'] == 0:
                continue
            #if row['s_code'] != 'sz002097':
                #continue

            res['sz_max'] += 1
            if row['chg'] > 0:
                res['sz_up'] += 1
                #是否涨停 昨日收盘价*1.1
                up_price = float(row['last_close']) * 1.1
                up_price = '{:.2f}'.format(Decimal(str(up_price)))
                #print up_price
                _res = {'m': 0, 'l': 0, 'k': 0}
                if row['last_close'] and row['high'] and row['close']:
                    if float(row['high']) == float(up_price):
                        _res['m'] = 1
                        #最高价==当前价
                        if row['high'] == row['close']:
                            _res['l'] = 1
                        else:
                            _res['k'] = 1

                if _res['m'] == 1:
                    res['zt_top'] += _res['m']
                    res['zt_last'] += _res['l']
                    res['zt_open'] += _res['k']
            else:
                res['sz_down'] += 1

        _has = self.mysql.fetch_one("select * from  s_daily_report where dateline=%s" % indate)
        _where = "dateline=%s" % indate
        if _has is not None:
            self.mysql.dbUpdate('s_daily_report', res, _where)
        else:
            self.mysql.dbInsert('s_daily_report', res)
        print res
