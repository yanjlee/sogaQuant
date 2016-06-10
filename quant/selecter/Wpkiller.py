#! -*- coding:utf-8 -*-
from quant.core.Selecter import *


class WpKillerSelecter(Selecter):
    '''
    跳开，冲高回落
    '''
    def __init__(self, setting):
        Selecter.__init__(self, setting)

    def run(self):
        today_select = self.todayDF[(self.todayDF.chg > 0) & (self.todayDF.chg < 9.8)]
        res = []
        for i in range(len(today_select)):
            item = today_select.iloc[i]
            #if item['s_code'] != 'sh600172':
                #continue
            #ST过滤
            ms = self.filter_code(item['name'])
            if ms:
                continue
            _yes_data = self.yestodayDF[self.yestodayDF['s_code'] == item['s_code']]
            if _yes_data.empty:
                continue
            #今天最低价大于昨天最高价、非一字板
            if item['low'] > _yes_data.iloc[0].high and item['open'] < item['last_close']*1.1:
                res.append(item['s_code'])
                print "%s==%s==%s======" % (item['s_code'], item['name'], item['chg'])
        return res
