# -*- coding: utf-8 -*-
import sys
import time
import re
from quant.tools.Util import sTools
from quant.core.DB import sMysql
from settings import *
import pandas


class Selecter(object):

    bk_start = 0
    bk_end = 0

    listDataHistory = None

    def __init__(self, name, setting):
        self.bk_start = time.clock()
        print sys.argv
        self.tools = sTools()
        self.init(setting)

    def __del__(self):
        self.bk_end = time.clock()
        time_str = "read: %f s" % (self.bk_end - self.bk_start)
        print time_str

    def format_code(self, code):
        item = {}
        item['s_code'] = code[0]
        item['code'] = code[1]
        item['dateline'] = code[2]
        item['chg_m'] = code[3]
        item['chg'] = code[4]
        item['open'] = code[5]
        item['close'] = code[6]
        item['high'] = code[7]
        item['low'] = code[8]
        item['last_close'] = code[9]
        item['name'] = code[10]
        return item

    def filter_code(self, codeName):
        ms = re.findall(re.compile(r'\*|N|ST'), codeName)
        return ms

    def ___set_universe(self, ids):
        #a = ['CYB', 'ZXB']
        _where = []
        resx = []
        for i in range(len(ids)):
            #print ids[i]
            if ids[i] == 'CYB':
                _where.append(" `code` LIKE '300%'")
            elif ids[i] == 'ZXB':
                _where.append(" `code` LIKE '002%'")
            else:
                resx.append(ids[i])

        if len(_where) > 0:
            temp = self.mysql.getRecord("select s_code from s_stock_list where %s " % (' OR '.join(_where)))
            l = len(temp)

            for i in range(0, l):
                resx.append(str(temp[i][0]))

        _codes = '","'.join(resx)

        ids_str = '"%s"' % _codes
        return ids_str

    def init(self, setting):
        self.mysql = sMysql(MYSQL_DB['host'], MYSQL_DB['user'], MYSQL_DB['password'], MYSQL_DB['dbname'])
        limit = 100
        if 'limit' in setting.keys():
            limit = setting['limit']

        _where = []

        if setting['start'] == setting['end']:
            _where.append(" dateline = %s" % setting['end'])
        else:
            last_day = " dateline = %s" % self.tools.d_date('%Y%m%d')
            if 'end' in setting.keys():
                last_day = " dateline <= %s" % setting['end']
            _where.append(last_day)

            if 'start' in setting.keys():
                _where.append(" dateline >= %s" % setting['start'])

        if 'universe' in setting.keys():
            s_codes = " s_code in(%s)" % self.___set_universe(setting['universe'])
            _where.append(s_codes)

        _wheres = ' AND '.join(_where)

        print "=======截止天数===%s====" % setting['end']

        date_sql = "select dateline FROM s_opening_day WHERE dateline <=%s order by dateline desc limit %s" % (setting['end'], limit)
        print date_sql
        temp = self.mysql.getRecord(date_sql)

        self.lastDay = temp[0][0]
        self.yestoday = temp[1][0]

        pandas.set_option('display.width', 200)
        sql_data = "select s_code,code,dateline,chg_m,chg,open,close,high,low,last_close,name FROM s_stock_trade WHERE %s " % _wheres
        print sql_data
        tmpdf = pandas.read_sql(sql_data, self.mysql.db)
        #print tmpdf
        #sys.exit()
        #历史除权数据计算
        if ('is_open_chuquan' in setting.keys()) and setting['is_open_chuquan']:
            self._chQ = self.getChuQuan()
            #print self._chQ
            #sys.exit()
            self.df = tmpdf.apply(self.format_chuquan_hanlder, axis=1)
            #print self.df
            #sys.exit()
        else:
            self.df = tmpdf
        self.todayDF = self.df[self.df.dateline == int(self.lastDay)]
        self.yestodayDF = self.df[self.df.dateline == int(self.yestoday)]
        #sys.exit()
        print "========init Days & init stock trader Done."

    def format_chuquan_hanlder(self, x):
        if x.s_code not in self._chQ.keys():
                return x

        code_chuquan = self._chQ[x.s_code]
        #print code_chuquan
        #sys.exit()
        for i in range(len(code_chuquan)):
            #print "========="
            #print _chQ[x.s_code][i]
            _fac = code_chuquan[i]['factor']
            if x.dateline > code_chuquan[i]['start'] and x.dateline <= code_chuquan[i]['end']:
                x.last_close = x.last_close * code_chuquan[i]['factor']
                if x.dateline == code_chuquan[i]['end']:
                    _fac = code_chuquan[i-1]['factor']
                x.open = x.open * _fac
                x.close = x.close * _fac
                x.high = x.high * _fac
                x.low = x.low * _fac
                #print x
                #sys.exit()
        return x

    def getChuQuan(self):
        '''获取历史除权数据,重写open and s_code in('sh600146','sz002527')'''
        chuQuan = pandas.read_sql("select s_code,dateline,factor from s_stock_fuquan where 1 order by dateline DESC", self.mysql.db)

        _chQ = {}
        _fa = 1
        if len(chuQuan) == 1:
            #print chuQuan.iloc[0].dateline
            _chQ[s_code] = []
            _chQ[s_code].append({'start': 0, 'end': chuQuan.iloc[0].dateline, 'factor': chuQuan.iloc[0].factor})
            _chQ[s_code].append({'start': chuQuan.iloc[0].dateline, 'end': tools.d_date('%Y%m%d'), 'factor': 1})

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
            '''
        return _chQ
        #print _chQ

    def run(self):
        raise NotImplementedError
