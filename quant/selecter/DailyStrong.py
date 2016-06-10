#! -*- coding:utf-8 -*-
from quant.core.Selecter import *
#from __future__ import division


class DailyStrongSelecter(Selecter):
    '''
    N天涨幅超过25%
    '''
    def __init__(self, setting):
        Selecter.__init__(self, setting)
        self.setting = setting

    def run(self):
        today_select = self.todayDF[self.todayDF.high > 5]

        res = []
        result = []
        #tofile = self.config['daily_log'] % self.tools.d_date('%Y%m%d')
        #fp = open(tofile, 'a+')
        if self.today != self.lastDay:
            sql_data = "select s_code,code,dateline,chg_m,chg,open,close,high,low,last_close,name,amount,run_market FROM s_stock_trade WHERE dateline=%s " % self.today
            tmpdf = pandas.read_sql(sql_data, self.mysql.db)
        else:
            tmpdf = []

        for code in today_select.values:
            item = self.format_code(code)
            #一字板不计入
            if item['high'] == item['low']:
                continue
            ms = self.filter_code(item['name'])
            if ms:
                continue

            #按时排列 取4天的振幅
            _one_stock = self.df[self.df['s_code'] == item['s_code']].sort_values(by=('dateline'), ascending=False)
            #print _one_stoc
            #为空或复牌第一天的过滤f['Age'].isnull() a.empty, a.bool(), a.item(), a.any() or a.all().
            if _one_stock.empty or len(_one_stock.index) < 2:
                continue

            #近几天的最低点
            mark_day = _one_stock.head(self.setting['limit']).sort_values(by=('low'), ascending=True)

            #前几天高点必须比今天低
            if mark_day.iloc[0].high < item['high'] and item['high'] > _one_stock.iloc[1].high:
                #print item
                up_precent = ((item['high'] - mark_day.iloc[0].low)/mark_day.iloc[0].low)*100

                #if up_precent >= 20 and item['chg'] > 0:
                if up_precent >= 24:
                    #print up_precent
                    res.append([code[0], str(code[2]), str(up_precent)])
                    result.append(item['s_code'])
                    curr = ''
                    if len(tmpdf):
                        curr = tmpdf[tmpdf.s_code == item['s_code']]
                        curr = curr.iloc[0].chg
                    print "%s==%s==%s====%s====%s=" % (item['s_code'], item['name'], item['chg'], int(up_precent), curr)
                    #loc = 0
                    #if item['s_code'][0:2] == 'sh':
                    #    loc = 1
                    #zxb = str(loc) + str(item['code']) + "\r\n"
                    #fp.write(zxb)
        return result
