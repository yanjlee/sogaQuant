# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
from decimal import Decimal
from quant.spider.TdxAnalyse import *
from quant.strategy.Average import *

from quant.core.DB import sMysql
from quant.tools.Util import sTools

from elasticsearch import Elasticsearch
from settings import *
mysql = sMysql(MYSQL_DB['host'], MYSQL_DB['user'], MYSQL_DB['password'], MYSQL_DB['dbname'])


def k_average(indate):
    a = Average()
    a.main_report(indate)


#每日收盘价在均线之上
def k_ma_count(indate):
    _data = mysql.getRecord("select s_code,dateline,ma5,ma10,ma20,ma30,ma60 from s_stock_average where dateline = %s" % indate)
    _st_data = mysql.getRecord("select s_code,close from s_stock_trade where dateline= %s" % indate)
    b = {}
    for i in range(len(_st_data)):
        b[str(_st_data[i][0])] = _st_data[i][1]

    for j in range(len(_data)):
        _d_c = b[_data[j][0]]
        #ma5
        sql = []
        if _d_c >= _data[j][2]:
            sql.append('on_ma5=on_ma5+1')
        if _d_c >= _data[j][3]:
            sql.append('on_ma10=on_ma10+1')
        if _d_c >= _data[j][4]:
            sql.append('on_ma20=on_ma20+1')
        if _d_c >= _data[j][5]:
            sql.append('on_ma30=on_ma30+1')
        if _d_c >= _data[j][6]:
            sql.append('on_ma60=on_ma60+1')

        #print "update s_daily_report set %s where dateline=%s" % (','.join(sql), indate)
        #print len(sql)
        #sys.exit()
        if len(sql) > 0:
            mysql.dbQuery("update s_daily_report set %s where dateline=%s" % (','.join(sql), indate))


def k_day_report(indate):
    '''
    _has = mysql.fetch_one("select * from  s_daily_report where dateline=%s" % indate)
    _has = mysql.getRecord("select * from s_stock_list where dateline=%s" % indate)
    for i in range(len(_has)):
        print _has[i]['status']
        sys.exit()

    print _has
    #print len(_has)
    if _has is None:
        print 11111

    #print len(_has)
    sys.exit()
    '''
    data = mysql.getRecord("select high,close,last_close,chg,s_code from s_stock_trade where dateline=%s" % indate)
    _data_lhb = mysql.getRecord("select s_code,yyb_id,B_volume,S_volume from s_lhb_days_detail where dateline=%s" % indate)
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

    for i in range(len(_data_lhb)):
        _s_s_code = _data_lhb[i][0]
        _s_yyb_id = _data_lhb[i][1]
        #一个票中营业部买入又卖出
        if len(_tmp) > 0 and _data_lhb[i][0] in _tmp.keys() and _s_yyb_id in _tmp[_data_lhb[i][0]]:
            continue
        if _s_yyb_id not in _tmp_yyb.keys():
            _tmp_yyb[_s_yyb_id] = []

        _cn = _data_lhb[i][2]-_data_lhb[i][3]
        _tmp_yyb[_s_yyb_id].append(_cn)

        if _s_s_code not in _tmp.keys():
            _tmp[_s_s_code] = []

        _tmp[_s_s_code].append(_s_yyb_id)

    if len(_tmp_yyb) > 0:
        for yyb_id, value in _tmp_yyb.items():
            x = sum(value)
            res['lhb_max'] += 1
            if x > 0:
                res['lhb_in'] += 1
            else:
                res['lhb_out'] += 1

    for i in range(len(data)):
        if data[i][0] == 0:
            continue
        #if data[i][4] != 'sz000420':
        #    continue
        res['sz_max'] += 1
        if data[i][3] > 0:
            res['sz_up'] += 1
            #是否涨停 昨日收盘价*1.1
            up_price = float(data[i][2]) * 1.1
            #print up_price
            up_price = '{:.2f}'.format(Decimal(str(up_price)))
            #print up_price
            #print data[i]
            #sys.exit()
            _res = {'m': 0, 'l': 0, 'k': 0}
            if data[i][2] and data[i][0] and data[i][1]:
                if float(data[i][0]) == float(up_price):
                    _res['m'] = 1
                    #最高价==当前价
                    if data[i][0] == data[i][1]:
                        _res['l'] = 1
                    else:
                        _res['k'] = 1
                        #print data[i][4]
            if _res['m'] == 1:
                res['zt_top'] += _res['m']
                res['zt_last'] += _res['l']
                res['zt_open'] += _res['k']
        else:
            res['sz_down'] += 1
    _has = mysql.fetch_one("select * from  s_daily_report where dateline=%s" % indate)
    #print res
    #sys.exit()
    _where = "dateline=%s" % indate
    if _has is not None:
        mysql.dbUpdate('s_daily_report', res, _where)
    else:
        mysql.dbInsert('s_daily_report', res)
    print res


def main_tdx():
    #date = 20160201
    print 10
    sys.exit()
    date = tools.d_date('%Y%m%d')
    ffile = '/Users/solomon/Downloads/008/%s.xls' % date
    tfile = '/Users/solomon/Downloads/008/%s.csv' % date

    a = TdxAnalyseSpider()
    a.init(ffile, tfile)


def main_factor(abc):
    os.system('php /htdocs/soga/trader/index.php Base get_fq_factor')


def main_elasticsearch():
    es = Elasticsearch(host="localhost", port="9200")
    tools = sTools()
    today = tools.d_date('%Y%m%d')
    #today = 20160112
    #print today
    #sys.exit()
    data = mysql.getRecord("select * from s_stock_list where dateline=%s " % today)

    tags = mysql.getRecord("select s_code,category_name from s_stock_cate_list where 1")
    tags_list = {}
    for i in range(len(tags)):
        if tags[i][0] not in tags_list.keys():
            tags_list[tags[i][0]] = [tags[i][1]]
        else:
            tags_list[tags[i][0]].append(tags[i][1])

    i = 1
    for row in data:
        row = list(row)
        tagss = ''
        if row[2] in tags_list.keys():
            tags_ids = tags_list[row[2]]
            tagss = ','.join(list(set(tags_ids)))
        #取财务指标
        s_code = row[2]
        #s_code = 'sh600836'
        tes = mysql.fetch_one("select * from s_company_finance where code=%s order by reportdate desc limit 1" % s_code[2:])

        if tes is None:
            tes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        average = mysql.fetch_one("select * from s_stock_average where s_code ='%s' and dateline=%s" % (s_code, today))
        if average is None:
            average = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        doc = {
            's_code': s_code,
            'name': row[6],
            'tagss': tagss,
            'last_close': row[8],
            'open': row[9],
            'close': row[10],
            'high': row[11],
            'low': row[12],
            'chg': row[13],
            'chg_m': row[14],
            'volumes': row[15]/100,
            'amount': row[16]/10000,
            'now_zf': row[17],
            'turnover': row[18],
            'run_market': row[19]/100000000,
            'all_market': row[20]/100000000,
            'reportdate': tes[2],
            'basiceps': tes[3],                 # 基本每股收益
            'epsweighted': tes[4],              # 每股收益(加权)
            'epsdiluted': tes[5],               # 每股收益(摊薄)
            'naps': tes[6],                     # 每股净资产
            'opercashpershare': tes[7],         # 每股现金流
            'peropecashpershare': tes[8],       # 每股经营性现金流
            'netassgrowrate': tes[9],           # 净资产增长率(%)
            'netincgrowrate': tes[13],          # 净利润增长率(%)
            'salegrossprofitrto': tes[15],      # 销售毛利率

            'on_ma5': average[4],
            'on_ma10': average[5],
            'on_ma20': average[6],
            'on_ma30': average[7],
            'on_ma60': average[8],
        }
        #print doc
        #sys.exit()
        es.index(index="stock8", doc_type='info', id=i, body=doc)
        #sys.exit()
        i += 1
    es.indices.refresh(index="stock8")


def main_while(abc):

    i = 1
    tools = sTools()
    today = tools.d_date('%Y%m%d')
    today = 20160226
    while True:
       # print i
        #os.system('php /htdocs/soga/trader/index.php Base daily_stock_list')
        _st_data = mysql.getRecord("select chg from s_stock_list where dateline= %s" % today)
        unixtime = datetime.datetime.now().strftime("%s")
        print unixtime
        #sys.exit()
        for i in range(len(_st_data)):
            chg = _st_data[i][0]
            #print chg
            #sys.exit()

            if chg <= -5:
                _type = 1
            elif chg > -5 and chg <= -3:
                _type = 2
            elif chg > -3 and chg <= 0:
                _type = 3
            elif chg > 0 and chg <= 3:
                _type = 4
            elif chg > 3 and chg <= 7:
                _type = 5
            else:
                _type = 6

            _has = mysql.fetch_one("select * from  s_status where s_t=%s" % unixtime)
            #print res
            #sys.exit()
            _where = "s_t=%s" % unixtime
            _field = "t_%s" % _type
            res = {'s_t': unixtime, _field: 1}
            #print res
            #sys.exit()
            if _has is not None:
                mysql.dbQuery('update s_status set %s=%s+1 where %s' % (_field, _field, _where))
            else:
                mysql.dbInsert('s_status', res)

        time.sleep(65)


if __name__ == '__main__':

    #main_dailyStrong(sys.argv[1])
    #main_tdx()
    #main_elasticsearch()
    function = eval(sys.argv[1])
    #print function
    #sys.exit()
    function(sys.argv[2])
    #main_factor()
