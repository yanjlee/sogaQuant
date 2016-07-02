# -*- coding: utf-8 -*-
import pandas
import hashlib
import math
from quant.core.Stats import *


class Average(StatsEngine):
    '''
    复权后的均线计算
    '''
    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        '''
        dateline=%s" % day
        '''
        day = self.args[2]
        pandas.set_option('display.width', 200)
        d2 = self.mysql.getRecord("select s_code from s_stock_list where dateline=%s" % day)
        for row in d2:
            s_code = row['s_code']
            #if s_code != 'sh600000':
            #    continue
            self._chQ = self.getChuQuan(s_code)
            sql_data = "select s_code,code,dateline,chg_m,chg,open,close,high,low,last_close,name FROM s_stock_trade WHERE s_code ='%s' and dateline >20150101 " % s_code
            print sql_data
            tmpdf2 = pandas.read_sql(sql_data, self.mysql.db)
            tmpdf = tmpdf2.apply(self.format_chuquan_hanlder, axis=1)
            tmpdf.sort_values(by=('dateline'), ascending=False)

            ma_list = [5, 10, 20, 30, 60]
            for ma in ma_list:
                tmpdf['MA_' + str(ma)] = pandas.rolling_mean(tmpdf['close'], ma)

            last5 = tmpdf.tail(60)
            #print last5
            #sys.exit()
            for i5 in range(0, len(last5)):
                if str(last5.iloc[i5].dateline) != day:
                    continue

                word = s_code[2:] + str(last5.iloc[i5].dateline)
                if math.isnan(last5.iloc[i5].MA_5):
                    break
                if math.isnan(last5.iloc[i5].MA_10):
                    break

                _m60 = last5.iloc[i5].MA_60
                if math.isnan(last5.iloc[i5].MA_60):
                    _m60 = 0
                else:
                    _m60 = round(_m60, 2)
                _m30 = last5.iloc[i5].MA_30
                if math.isnan(last5.iloc[i5].MA_30):
                    _m30 = 0
                else:
                    _m30 = round(_m30, 2)

                item = {}
                item['s_code'] = s_code
                item['dateline'] = last5.iloc[i5].dateline
                item['hash'] = hashlib.md5(word).hexdigest()
                item['ma5'] = round(last5.iloc[i5].MA_5, 2)
                item['ma10'] = round(last5.iloc[i5].MA_10, 2)
                item['ma20'] = round(last5.iloc[i5].MA_20, 2)
                item['ma30'] = _m30
                item['ma60'] = _m60
                self.mysql.dbInsert('s_stock_average', item)

    def getChuQuan(self, s_code):
        '''获取历史除权数据,重写open and s_code in('sh600365')'''
        chuQuan = pandas.read_sql("select s_code,dateline,factor from s_stock_fuquan where 1 and s_code in('%s') order by dateline DESC" % s_code, self.mysql.db)

        _chQ = {}
        _fa = 1
        #只有一条记录的特殊处理
        if len(chuQuan) == 1:
            print chuQuan.iloc[0].dateline
            _chQ[s_code] = []
            _chQ[s_code].append({'start': 0, 'end': chuQuan.iloc[0].dateline, 'factor': chuQuan.iloc[0].factor})
            _chQ[s_code].append({'start': chuQuan.iloc[0].dateline, 'end': self.tools.d_date('%Y%m%d'), 'factor': 1})

        else:
            for i in range(len(chuQuan)):
                s_code, dateline, factor = chuQuan.iloc[i]
                if s_code not in _chQ.keys():
                    _chQ[s_code] = []
                    _select = chuQuan[chuQuan.s_code == s_code]
                    for j in range(len(_select)):
                        if j == 0:
                            _chQ[s_code].append({'start': _select.iloc[j].dateline, 'end': self.tools.d_date('%Y%m%d'), 'factor': 1})
                        else:
                            _fa *= _select.iloc[j-1].factor
                            _chQ[s_code].append({'start': _select.iloc[j].dateline, 'end': _select.iloc[j-1].dateline, 'factor': _fa})
                            if j == len(_select)-1:
                                _fa *= _select.iloc[j].factor
                                _chQ[s_code].append({'start': 0, 'end': _select.iloc[j].dateline, 'factor': _fa})
        #sys.exit()
        '''
        s_code  dateline  factor
        0  sz002422  20150722  0.4971
        1  sz002422  20140701  0.6625
        2  sz002422  20130521  0.9959
        3  sz002422  20120615  0.9949
        4  sz002422  20110429  0.4980
        {'sz002422': [{'start': 20150722, 'end': '20151223', 'factor': 1},
        {'start': 20140701, 'end': 20150722, 'factor': 0.49709999999999999},
        {'start': 20130521, 'end': 20140701, 'factor': 0.32932875},
        {'start': 20120615, 'end': 20130521, 'factor': 0.32797850212500002},
        {'start': 20110429, 'end': 20120615, 'factor': 0.32630581176416251},
        {'start': 0, 'end': 20110429, 'factor': 0.16250029425855292}]}


        {'sh603885': [{'start': 20151228, 'end': '20160107', 'factor': 1}]}
        '''
        return _chQ

    _chQ = {}

    def format_chuquan_hanlder(self, x):
        if x.s_code not in self._chQ.keys():
                return x

        code_chuquan = self._chQ[x.s_code]
        for i in range(len(code_chuquan)):
            _fac = code_chuquan[i]['factor']
            if x.dateline > code_chuquan[i]['start'] and x.dateline <= code_chuquan[i]['end']:
                x.last_close = x.last_close * code_chuquan[i]['factor']
                if x.dateline == code_chuquan[i]['end']:
                    _fac = code_chuquan[i-1]['factor']
                x.open = x.open * _fac
                x.close = x.close * _fac
                x.high = x.high * _fac
                x.low = x.low * _fac
        return x
