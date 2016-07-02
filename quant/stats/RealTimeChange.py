# -*- coding: utf-8 -*-
import time
import datetime
from quant.core.Stats import *


class RealTimeChange(StatsEngine):
    '''
    每5分钟获取一次当日开盘个股涨跌,用于观察市场整体热度
    '''
    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        today = self.tools.d_date('%Y%m%d')

        while True:
            '''
            block_time = int(self.tools.d_date('%H%M%S'))
            if (block_time > 113000 and block_time < 130000) or block_time > 153000 or block_time < 93000:
                print "%s====Market Close;" % block_time
                time.sleep(120)
                continue
            '''
            is_opening = self.is_opening()
            if is_opening is False:
                print "RealTimeChange===Market Close===%s===;" % self.tools.d_date('%H%M%S')
                time.sleep(30)
                continue

            #os.system('php /htdocs/quant/soga/mv/index.php Base daily_stock_list')
            self.run_php('Base daily_stock_list')
            _st_data = self.mysql.getRecord("select chg from s_stock_list where dateline= %s" % today)
            unixtime = datetime.datetime.now().strftime("%s")
            #print block_time
            for row in _st_data:
                chg = row['chg']

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

                _has = self.mysql.fetch_one("select * from  s_status where s_t=%s" % unixtime)

                _where = "s_t=%s" % unixtime
                _field = "t_%s" % _type
                res = {'s_t': unixtime, _field: 1}

                if _has is not None:
                    self.mysql.dbQuery('update s_status set %s=%s+1 where %s' % (_field, _field, _where))
                else:
                    self.mysql.dbInsert('s_status', res)

            time.sleep(300)
