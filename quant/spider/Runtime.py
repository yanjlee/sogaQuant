# -*- coding: utf-8 -*-
'''
Tdx分时异动
'''
#import sys
import pymongo
import hashlib
from datetime import date, datetime
from quant.core.Spider import *


class RuntimeSpider(SpiderEngine):

    def get_data(self):
        MONGO_IP = '192.168.5.106'
        URL = 'http://hq.sinajs.cn/?func=getData._hq_cron();&list=sh600836,sz300190'
        client = pymongo.MongoClient(MONGO_IP, 27017)
        db = client.spider

        data = self.sGet(URL, 'utf8', 'de')
        data = data.split('";')

        l = len(data)
        resx = []
        for i in range(0, l-1):
            res = data[i].split(',')
            #continue
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
            a = item.values()
            word = '-'.join(a)
            item['hash'] = hashlib.md5(word).hexdigest()
            resx.append(item)

        db.run_time.insert(resx)
