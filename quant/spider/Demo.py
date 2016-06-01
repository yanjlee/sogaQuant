# -*- coding: utf-8 -*-
import sys
import time
import datetime
import logging
import httplib
import requests
from quant.core.Spider import *


class DemoSpider(SpiderEngine):
    '''
    更新指数
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def run(self):
        self.tools.setup_logging(sys.argv[1], True, True)

        logging.debug('Start Daily 000001 & 399006 Data=====Days:%s ' % sys.argv[2])
        quncms_db = self.config['mysql']['quncms']
        self.mysql2 = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

    def shtic_data(self):
        i = 9874
        while 1:
            if i > 15000:
                break
            url = "http://cydsbm.shtic.com/admin/ProjectInfo/Index?id=%s" % i
            st = requests.get(url)
            code = st.status_code
            if code == 500:
                i += 1
                continue
            a = self.sMatch('<td colspan="5" style="width: 80%">', '<\/td>', st.text, 0)

            if len(a) == 0:
                i += 1
                continue
            a = self.sTags(a[0])
            b = self.sMatch('<td colspan="5">', '<\/td>', st.text, 0)

            ai = {
                'xid': url,
                'title': a,
                'keywords': self.sTags(b[17]),
                'vdesc': self.sTags(b[9]),
            }
            if len(ai['title']) == 0 or len(ai['keywords']) == 0 or len(ai['vdesc']) == 0:
                i += 1
                continue
            i += 1
            print "%s===%s" % (i, a)
            self.mysql2.dbInsert('qiye', ai)
