# -*- coding: utf-8 -*-
import hashlib
import commands
import memcache
from datetime import date, datetime
from quant.core.Spider import *


class HandicapSpider(SpiderEngine):
    '''
    5档盘口
    '''
    def run(self, mysql):
        vid = int(sys.argv[2])

        out_put = '/usr/bin/php /htdocs/quant/soga/stock.php %s' % vid
        _data = commands.getoutput(out_put)

        URL = 'http://hq.sinajs.cn/?func=getData._hq_cron();&list=%s' % _data
        #URL = 'http://hq.sinajs.cn/?func=getData._hq_cron();&list=sh600749'

        self.mcache = memcache.Client(['127.0.0.1:11211'])

        is_opening = self.is_opening()
        if is_opening is False:
            print "GetFiveHandicap===Market Close===%s===;" % self.tools.d_date('%H%M%S')
            time.sleep(30)
            return False

        self.today = self.tools.d_date('%Y%m%d')
        #print self.today
        #sys.exit()
        data = self.sGet(URL, 'utf-8')
        data = data.split('";')

        l = len(data)
        for i in range(0, l-1):
            if len(data[i]) < 30:
                continue
            res = data[i].split(',')

            if int(res[8]) == 0:
                continue

            _tmp = res[0].split('=')
            xcode = _tmp[0].replace('var hq_str_', '')
            item = {}
            item['dateline'] = datetime.strftime(date.today(), "%Y%m%d")
            item['s_code'] = xcode.replace("\n", "")
            item['all_volume'] = res[8]
            item['all_money'] = res[9]
            item['B_1_price'] = res[11]
            item['B_1_volume'] = res[10]
            item['B_2_price'] = res[13]
            item['B_2_volume'] = res[12]
            item['B_3_price'] = res[15]
            item['B_3_volume'] = res[14]
            item['B_4_price'] = res[17]
            item['B_4_volume'] = res[16]
            item['B_5_price'] = res[19]
            item['B_5_volume'] = res[18]
            item['S_1_price'] = res[21]
            item['S_1_volume'] = res[20]
            item['S_2_price'] = res[23]
            item['S_2_volume'] = res[22]
            item['S_3_price'] = res[25]
            item['S_3_volume'] = res[24]
            item['S_4_price'] = res[27]
            item['S_4_volume'] = res[26]
            item['S_5_price'] = res[29]
            item['S_5_volume'] = res[28]

            item['min_sec'] = res[31].replace(':', '')
            item['date_str'] = "%s %s" % (res[30], res[31])
            a = item.values()
            word = '-'.join(a)
            #item['hash'] = ''
            #item['hash'] = hashlib.md5(word).hexdigest()
            _hash = hashlib.md5(word).hexdigest()
            has = self.mcache.get(_hash)
            if has:
                continue

            table = 's_stock_runtime_%s' % item['dateline']
            aitem = mysql.dbInsert(table, item)
            item['id'] = aitem['LAST_INSERT_ID()']
            self.mcache.set(_hash, 1, 66400)

            _t_hash = "%s==%s" % (self.today, item['s_code'])
            stock = self.mcache.get(_t_hash)
            if stock:
                _top = float(stock['last_close']) * 1.1
                _bottom = float(stock['last_close']) * 0.9
                #print "==%s====%s=" % (round(_top, 2), _bottom)
                if (float(item['B_1_price']) == round(_top, 2)) or (float(item['S_1_price']) == round(_bottom, 2)):
                    return False
                else:
                    self.__filter_big_order(item)

    def __filter_big_order(self, x):
        stem = 13000000
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
            '''
            _top = float(stock['last_close']) * 1.1
            _bottom = float(stock['last_close']) * 0.9
            #print "==%s====%s=" % (round(_top, 2), _bottom)
            if (x['B_1_price'] == round(_top, 2)) or (x['S_1_price'] == round(_bottom, 2)):
                return False
            '''
            a = {
                'dateline': self.today,
                'date_str': x['date_str'],
                's_code': x['s_code'],
                'view_id': x['id'],
                'b_amount': int(b_money/10000),
                's_amount': int(s_money/10000)
            }
            #已涨跌停的跳过
            #_top = float(stock['last_close']) * 1.1
            #_bottom = float(stock['last_close']) * 0.9

            #if (float(stock['close']) == round(_top, 2)) or (float(stock['close']) == round(_bottom, 2)):
            #    return True
            #print a
            #sys.exit()
            #同一分钟买卖盘去重
            #word = "%s-%s-%s" % (d_str[0:-2], a['s_amount'], a['b_amount'])
            word = d_str[0:-3]
            word = "%s=%s" % (word, x['s_code'])
            word = hashlib.md5(word).hexdigest()

            _has = self.mysql.fetch_one("select * from  s_stock_runtime_snap where hash_str='%s'" % word)
            if _has is None:
                a['hash_str'] = word
                self.mysql.dbInsert('s_stock_runtime_snap', a)
