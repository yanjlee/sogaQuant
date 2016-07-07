# -*- coding: utf-8 -*-
import hashlib
import re
from quant.core.Stats import *


class Pankou(StatsEngine):
    '''
    实时盘口统计
    '''
    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def __filter_code(self, stock):
        #过滤代码,符合条件返回true
        '''
        流通盘>400亿
        名称中有N|ST|航空|银行
        上市日期
        不是涨停或跌停
        '''
        res = False
        ms = re.findall(re.compile(r'\*|N|ST|航空|银行'), stock['name'])
        t = time.time()-60*86400
        listing_date = self.tools.d_date('%Y%m%d', t)
        #listing_date = 20151230
        if stock['run_market'] > 40000000000 or stock['listing_date'] == 0 or stock['listing_date'] > listing_date or ms:
            res = True
        _top = float(stock['last_close']) * 1.1
        _bottom = float(stock['last_close']) * 0.9

        #涨跌停一定有大单,跳转
        if (float(stock['close']) == round(_top, 2)) or (float(stock['close']) == round(_bottom, 2)):
            res = True
        return res

    def run(self):
        today = self.tools.d_date('%Y%m%d')
        self.today = sys.argv[2]
        ax = self.mysql.getRecord("select s_code,code,close,last_close,listing_date,run_market,name,chg from s_stock_list where dateline=%s" % self.today)
        self._filter_code = []
        self._list_code = {}
        for i in range(0, len(ax)):
            if self.__filter_code(ax[i]):
                self._filter_code.append(ax[i]['s_code'])
                continue

            self._list_code[ax[i]['s_code']] = ax[i]

        aid = 0
        while 1:
            sql_data = "select * from s_stock_runtime_%s where id > %s limit 500" % (today, aid)
            #sql_data = "select * from s_stock_runtime_20160624 where s_code='sz002040' "
            tmpdf = self.mysql.getRecord(sql_data)

            if len(tmpdf) == 0:
                break

            for k in range(0, len(tmpdf)):
                aid = tmpdf[k]['id']
                if tmpdf[k]['s_code'] not in self._list_code.keys():
                    continue
                if float(self._list_code[tmpdf[k]['s_code']]['chg']) > 9.7:
                    continue
                self.__filter_big_order(tmpdf[k])

            print aid
            #sys.exit()

    def realtime(self):
        #实时统计
        #python realtime.py realtime_pankou 2
        today = self.tools.d_date('%Y%m%d')
        #today = 20160629
        maxnums = 0
        while True:
            ax = self.mysql.getRecord("select * from s_stock_runtime_snap where dateline=%s order by id ASC" % today)

            for i in range(maxnums, len(ax)):
                #判断是否已经涨停或跌停不再提示
                stock = self.mysql.fetch_one("select s_code,code,close,last_close,listing_date,run_market,name,chg from s_stock_list where s_code='%s'" % ax[i]['s_code'])
                #if stock['s_code'] != 'sz002695':
                #    continue
                if self.__filter_code(stock):
                    continue
                print "%s===%s|%s===B%s====S%s" % (ax[i]['date_str'], ax[i]['s_code'], stock['name'], ax[i]['b_amount'], ax[i]['s_amount'])
            maxnums = len(ax)
            time.sleep(2)

    def __filter_big_order(self, x):
        if x['s_code'] in self._filter_code:
            return False

        stem = 15000000
        b1_m = int(float(x['B_1_volume']) * float(x['B_1_price']))
        b2_m = int(float(x['B_2_volume']) * float(x['B_2_price']))
        b3_m = int(float(x['B_3_volume']) * float(x['B_3_price']))
        b4_m = int(float(x['B_4_volume']) * float(x['B_4_price']))
        b5_m = int(float(x['B_5_volume']) * float(x['B_5_price']))
        b_money = 0
        b1_money = b2_money = b3_money = b4_money = b5_money = 0
        if b1_m > stem:
            b1_money = b1_m
        if b2_m > stem:
            b2_money = b2_m
        if b3_m > stem:
            b3_money = b3_m
        if b4_m > stem:
            b4_money = b4_m
        if b5_m > stem:
            b5_money = b5_m

        b_money = max(b1_money, b2_money, b3_money, b4_money, b5_money)

        s1_m = int(float(x['S_1_volume']) * float(x['S_1_price']))
        s2_m = int(float(x['S_2_volume']) * float(x['S_2_price']))
        s3_m = int(float(x['S_3_volume']) * float(x['S_3_price']))
        s4_m = int(float(x['S_4_volume']) * float(x['S_4_price']))
        s5_m = int(float(x['S_5_volume']) * float(x['S_5_price']))
        s_money = 0
        s1_money = s2_money = s3_money = s4_money = s5_money = 0
        if s1_m > stem:
            s1_money = s1_m
        if s2_m > stem:
            s2_money = s2_m
        if s3_m > stem:
            s3_money = s3_m
        if s4_m > stem:
            s4_money = s4_m
        if s5_m > stem:
            s5_money = s5_m
        s_money = max(s1_money, s2_money, s3_money, s4_money, s5_money)
        d_str = str(x['date_str'])
        if b_money > 1 or s_money > 1:
            a = {
                'dateline': self.today,
                'date_str': x['date_str'],
                's_code': x['s_code'],
                'view_id': x['id'],
                'b_amount': int(b_money/10000),
                's_amount': int(s_money/10000)
            }
            #print a
            #return True
            #同一分钟买卖盘去重
            word = d_str[0:-3]
            word = "%s=%s" % (word, x['s_code'])
            word = hashlib.md5(word).hexdigest()

            _has = self.mysql.fetch_one("select * from  s_stock_runtime_snap_3 where hash_str='%s'" % word)
            if _has is None:
                a['hash_str'] = word
                self.mysql.dbInsert('s_stock_runtime_snap_3', a)
