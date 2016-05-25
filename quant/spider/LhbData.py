# -*- coding: utf-8 -*-
import sys
import time
import datetime
import logging
import pandas
from quant.core.Spider import *


class LhbDataSpider(SpiderEngine):
    '''
    更新营业部数据
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def get_info(self, yyb_id):
        self.get_daily_detail(yyb_id, sys.argv[2])

    def run(self):
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)

        #self.get_yyb_data(80138150)
        #sys.exit()

        logging.debug('Start Daily Lhb=====Days:%s ' % sys.argv[2])
        self.daily_lhb(sys.argv[2])
        #sys.exit()

        logging.debug('Start Daily Lhb=====Detail:%s ' % sys.argv[2])
        day_list = self.mysql.getRecord("SELECT * FROM s_lhb_days WHERE status=0 and dateline=%s" % sys.argv[2])
       # datas = []
        for i in range(0, len(day_list)):
            self.get_daily_jqk_detail(day_list[i], sys.argv[2])
            #time.sleep(5)
        '''
        logging.debug('Start Daily Lhb=====New YYB:%s ' % sys.argv[2])
        sql_data = "select yyb_id from s_lhb_days_detail where 1 group by yyb_id"
        tmpdf = pandas.read_sql(sql_data, self.mysql.db)

        has_yyb = pandas.read_sql("select * from s_lhb where name!=''", self.mysql.db)
        has = []
        for code in has_yyb.values:
            has.append(code[1])

        for xd in tmpdf.values:
            if xd[0] == 0 or xd[0] == 8888:
                continue
            if xd[0] not in has:
                self.get_yyb_data(xd[0])
        '''

    def get_daily_jqk_detail(self, s_data, dateline):
        s_code = s_data['s_code']
        d = datetime.datetime.strptime(dateline, "%Y%m%d")
        days = self.tools.d_date('%Y-%m-%d', time.mktime(d.timetuple()))
        url = "http://data.10jqka.com.cn/market/lhbcjmx/code/%s/date/%s/ajax/1" % (s_code[2:10], days)
        url = "http://data.10jqka.com.cn/market/lhbcjmx/code/603779/date/2016-05-16/ajax/1"

        logging.debug('Detail=====:%s ' % url)
        _data = self.sGet(url)
        _tr = self.sMatch(u'成交量：', u"总成交金额：", _data, 1)
        if _tr is None:
            return 1
        _td = self.sMatch(u'涨跌幅：', u'换手率：', _data, 1)
        _tp = self.sMatch(u'总成交金额：', u'万元', _data, 1)
        _hands = _tr[0].replace(u'万股', '')
        _hands = _hands.replace(' ', '')
        _hands = float(_hands)*10000
        _h_p = _tp[0].replace(' ', '')
        _h_p = float(_h_p)*10000
        indata = {
            'v_hands': _hands,
            'ud': _td[0],
            'volume': _h_p,
            'status': 1
        }
        code = s_code.lower()
        _where = " dateline=%s AND s_code='%s'" % (dateline, code)
        #self.mysql.dbUpdate('s_lhb_days', indata, _where)
        #print indata
        _f_table = self.sMatch('<table class="m_table">', '<\/table>', _data, 0)

        _xx_1 = self.sMatch('<tr(.*?)>', "<\/tr>", _f_table[0], 0)
        #print _xx_1[8]
        #sys.exit()
        #self.__format_datail2(dateline, s_code, _xx_1, 'B', 2, 1)
        #self.__format_datail2(dateline, s_code, _xx_1, 'B', 3, 2)

        self.__format_datail2(dateline, s_code, _xx_1, 'B', 4, 3)
        '''
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 5, 4)
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 6, 5)

        self.__format_datail2(dateline, s_code, _xx_1, 'B', 8, 1)
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 9, 2)
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 10, 3)
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 11, 4)
        self.__format_datail2(dateline, s_code, _xx_1, 'B', 12, 5)
        '''
        #sys.exit()

    def __format_datail2(self, dateline, code, html, o_type='B', i=0, sort=1):
        yyb_id = 8888
        if len(html) <= i:
            return False
        tdhtml = self.sMatch('<td(.*?)>', "<\/td>", html[i][1], 0)
        print html[i]
        sys.exit()
        #print tdhtml
        #print tdhtml[1][1]

        if tdhtml[1][1].find(u'机构专用') < 0:
            _c1 = self.sMatch('<a(.*?)>', '<\/a>', tdhtml[1][1], 0)
            if len(_c1) == 0:
                return False
            yyb_id = self.__find_yyb_id(_c1[0][1])

        _B = self.tools.strip_tags(tdhtml[2][1])
        if _B == '-':
            _B = 0

        _S = self.tools.strip_tags(tdhtml[4][1])
        if _S == '-':
            _S = 0
        _in_data = {
            'type': o_type,
            'dateline': dateline,
            's_code': code,
            'yyb_id': yyb_id,
            'B_volume': float(_B) * 10000,
            'B_p': self.tools.strip_tags(tdhtml[3][1]),
            'S_volume': float(_S) * 10000,
            'S_p': self.tools.strip_tags(tdhtml[5][1]),
            's_sort': sort
        }
        print _in_data
        #sys.exit()
        self.mysql.dbInsert('s_lhb_days_detail', _in_data)
        return _in_data

    def __find_yyb_id(self, name):
        day_list = self.mysql.fetch_one("SELECT * FROM s_lhb WHERE name='%s'" % name)
        if day_list is not None:
            return day_list['codex']
        else:
            res = {
                'codex': 1,
                'name': name,
                'province': '',
                'city': ''
            }
            self.mysql.dbInsert('s_lhb', res)
            return 1

    def get_daily_detail(self, s_data, dateline):
        s_code = s_data['s_code']
        d = datetime.datetime.strptime(dateline, "%Y%m%d")
        days = self.tools.d_date('%Y-%m-%d', time.mktime(d.timetuple()))
        url = "http://data.eastmoney.com/stock/lhb,%s,%s.html" % (days, s_code[2:10])
        #url = "http://data.eastmoney.com/stock/lhb,2016-03-30,000534.html"
        logging.debug('Detail=====:%s ' % url)
        _data = self.sGet(url)
        #self.tools.sWrite(_data, '/tmp/abc.log')
        #return 1
        #out_put = '/usr/bin/php /htdocs/quant/c.php %s' % base64.b64encode(url)
        #print out_put
        #_data = commands.getoutput(out_put)
        #print _data
        _tr = self.sMatch(u'成交量：', u"成交金额：", _data, 1)
        _td = self.sMatch(u'涨跌幅：', u'成交量：', _data, 1)
        log_file = '/Users/solomon/Downloads/%s.log' % days

        if _tr is None:
            self.tools.sWrite(_data, log_file)
            self.mysql.dbUpdate('s_lhb_days', {'status': 1}, "id=%s" % s_data['id'])
            return 1
        #print _tr
        #sys.exit()
        if _tr is not None:
            _hands = _tr[0].replace(u'万手', '')
            _hands = _hands.replace('&nbsp;', '')
            _hands = float(_hands)*10000
            ud = 0
            if _tr is not None:
                if len(_td) > 0:
                    ud = _td[0].replace(u'万手', '')
                    ud = ud.replace('&nbsp;', '')
            code = s_code.lower()
            indata = {
                'v_hands': _hands,
                'ud': ud,
                'status': 1
            }
            _where = " dateline=%s AND s_code='%s'" % (dateline, code)
            self.mysql.dbUpdate('s_lhb_days', indata, _where)

            _tables_1 = self.sMatch('<table cellpadding="0" cellspacing="0" class="default_tab stock-detail-tab" id="tab-2">', '<\/table>', _data, 0)
            _xx_1 = self.sMatch('<tr(.*?)>', "<\/tr>", _tables_1[0], 0)

            self.__format_datail(dateline, s_code, _xx_1, 'B', 2, 1)
            self.__format_datail(dateline, s_code, _xx_1, 'B', 3, 2)
            self.__format_datail(dateline, s_code, _xx_1, 'B', 4, 3)
            self.__format_datail(dateline, s_code, _xx_1, 'B', 5, 4)
            self.__format_datail(dateline, s_code, _xx_1, 'B', 6, 5)

            _tables_2 = self.sMatch('<table cellpadding="0" cellspacing="0" class="default_tab tab-2" id="tab-4">', '<\/table>', _data, 0)
            _xx_2 = self.sMatch('<tr(.*?)>', "<\/tr>", _tables_2[0], 0)

            self.__format_datail(dateline, s_code, _xx_2, 'S', 2, 1)
            self.__format_datail(dateline, s_code, _xx_2, 'S', 3, 2)
            self.__format_datail(dateline, s_code, _xx_2, 'S', 4, 3)
            self.__format_datail(dateline, s_code, _xx_2, 'S', 5, 4)
            self.__format_datail(dateline, s_code, _xx_2, 'S', 6, 5)

    def __format_datail(self, dateline, code, html, o_type='B', i=0, sort=1):
        yyb_id = 8888
        if len(html) <= i:
            return False
        tdhtml = self.sMatch('<td(.*?)>', "<\/td>", html[i][1], 0)
        if tdhtml[1][1].find(u'机构专用') < 0:
            _c1 = self.sMatch('<a href="\/stock\/lhb\/yyb\/(.*?)\.html">', '<\/a>', tdhtml[1][1], 0)
            if len(_c1) == 0:
                return False
            yyb_id = _c1[0][0]

        _B = self.tools.strip_tags(tdhtml[2][1])
        if _B == '-':
            _B = 0

        _S = self.tools.strip_tags(tdhtml[4][1])
        if _S == '-':
            _S = 0
        _in_data = {
            'type': o_type,
            'dateline': dateline,
            's_code': code,
            'yyb_id': yyb_id,
            'B_volume': float(_B) * 10000,
            'B_p': self.tools.strip_tags(tdhtml[3][1]),
            'S_volume': float(_S) * 10000,
            'S_p': self.tools.strip_tags(tdhtml[5][1]),
            's_sort': sort
        }
        print _in_data
        self.mysql.dbInsert('s_lhb_days_detail', _in_data)
        return _in_data

    def get_yyb_data(self, yyb_id):
        url = "http://data.eastmoney.com/stock/lhb/yyb/%s.html" % yyb_id
        logging.debug('GetUrl:%s ' % url)
        _data = self.sGet(url)
        _xxt = self.sMatch('<div class="tit">', '<\/div>', _data, 0)
        #print _xxt
        #sys.exit()
        _xxt2 = _xxt[0].strip().split(' ')
        if(_xxt2[0] == u'机构专用'):
            return False

        _has = self.mysql.fetch_one("select * from  s_lhb where codex=%s" % yyb_id)
        _where = "codex=%s" % yyb_id
        res = {
            'codex': yyb_id,
            'name': _xxt2[0],
            'province': '',
            'city': ''
        }
        #print res
        #sys.exit()
        if _has is not None:
            self.mysql.dbUpdate('s_lhb', res, _where)
        else:
            self.mysql.dbInsert('s_lhb', res)
        print res

    def daily_lhb(self, dateline):
        #每日上榜
        d = datetime.datetime.strptime(dateline, "%Y%m%d")
        days = self.tools.d_date('%Y-%m-%d', time.mktime(d.timetuple()))
        #url = "http://data.eastmoney.com/stock/lhb/%s.html" % days
        #url = 'http://data.eastmoney.com/stock/tradedetail.html'
        #url = 'http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate=%s,endDate=%s,gpfw=0,js=var data_tab_1.html' % (days, days)
        #url = 'http://data.eastmoney.com/'
        url = 'http://data.10jqka.com.cn/market/longhu/date/%s/' % days
        logging.debug('GetUrl:%s ' % url)

        _data = self.sGet(url)
        _tr = self.sMatch('<td class="tip-trigger " code="(.*?)">', '<\/td>', _data, 0)
        for i in range(0, len(_tr)):

            s_code = _tr[i][0]
            _prx = s_code[0:1]
            if int(_prx) not in [0, 3, 6]:
                continue
            if int(_prx) == 0 or int(_prx) == 3:
                s_code = 'sz%s' % s_code
            else:
                s_code = 'sh%s' % s_code

            indata = {
                'dateline': dateline,
                's_code': s_code,
                'v_hands': 0,
                'ud': 0,
                'volume': 0,
                's_reason': ''
            }
            _has = self.mysql.fetch_one("select * from  s_lhb_days where s_code='%s' and dateline=%s" % (indata['s_code'], dateline))
            if _has is None:
                #print indata
                self.mysql.dbInsert('s_lhb_days', indata)
