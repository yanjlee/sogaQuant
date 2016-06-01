# -*- coding: utf-8 -*-
import sys
import logging
import memcache
import hashlib
import time
from quant.core.Spider import *


class MinDataSpider(SpiderEngine):
    '''
    分钟数据下载
    选出龙头板块
    获取股票的主题
    取最近涨幅，成交量大的
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def get_info(self, s_code):
        #self.get_minute_from_qq(s_code)
        self.get_minute_from_sina(s_code)

    def run(self):
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)
        '''
        logging.info('start looping, args: %s' % sys.argv)
        logging.exception('Fail to read data.')
        logging.debug('save debug ')
        logging.warn('save warning ')
        return 1

        MONGO_IP = '127.0.0.1'
        client = pymongo.MongoClient(MONGO_IP, 27017)
        self.mango_db = client.spider
        '''
        self.mc = memcache.Client(['127.0.0.1:11211'])

        while not self.interrupted:
            block_time = int(self.tools.d_date('%H%M%S'))
            if (block_time > 113000 and block_time < 130000) or block_time > 153000 or block_time < 93000:
                logging.info("Market Close")
                time.sleep(120)
                continue
            datas = []
            logging.info("Market Open %s" % block_time)
            data = self.mysql.getRecord("select * from s_stock_list where dateline=%s " % self.today)

            for row in data:
                datas.append(row['s_code'])
            self.run_worker(datas)
            time.sleep(1000)

    def get_minute_from_sina(self, s_code):
        url = "http://vip.stock.finance.sina.com.cn/quotes_service/view/vML_DataList.php?asc=j&symbol=%s&num=1000" % s_code
        _data = self.sGet(url, 'utf8')
        _data = _data.replace('var minute_data_list = [[', '')
        _data = _data.replace(']];', '')
        _data = _data.replace("'", '')

        data = _data.split('],[')
        for i in range(0, len(data)):
            #以data[i]为key 标记数据是否已入库
            tmp = data[i].split(',')
            indata = {
                's_code': s_code,
                'dateline': str(self.today),
                'date_min': tmp[0].replace(':', '')
            }
            word = '-'.join(indata.values())
            value = self.mc.get(str(word))
            #value = None
            if value is None:
                indata['price'] = tmp[1]
                indata['volumes'] = tmp[2]
                indata['hash'] = hashlib.md5(word).hexdigest()
                self.mysql.dbInsert('s_stock_minute', indata)
                #self.mango_db.run_time.insert(indata)
                self.mc.set(str(word), 1, 86400)

    def get_minute_from_qq(self, s_code):
        url = "http://data.gtimg.cn/flashdata/hushen/minute/%s.js" % s_code
        _data = self.sGet(url, 'utf8')
        _data = _data.replace('";', '')
        data = _data.split('\\n\\')

        for i in range(0, len(data)):
            if i < 2 or data[i] is None:
                continue
            tmp = data[i].split(' ')
            if i == 2:
                vol = tmp[2]
            else:
                vol = tmp[2] - data[i-1][2]
            dmin = "%s00" % tmp[0]
            indata = {
                's_code': s_code,
                'dateline': self.today,
                'date_min': dmin
            }
            word = '-'.join(indata.values())
            value = self.mc.get(str(word))
            if value is None:
                indata['price'] = tmp[1]
                indata['volumes'] = vol
                indata['hash'] = hashlib.md5(word).hexdigest()
                self.mysql.dbInsert('s_stock_minute', indata)
                self.mc.set(str(word), 1, 86400*2)
