#! -*- coding:utf-8 -*-
from quant.core.Selecter import *


class DailyTrendSelecter(Selecter):
    '''
    指定时间内的高低点,判断当前处于超跌还是超买
    '''
    def __init__(self, setting):
        Selecter.__init__(self, setting)
        self.setting = setting

    def run(self):
        '''
        3天涨幅超过25%,回调13 18买点

        '''
        today_select = self.todayDF[self.todayDF.high > 8]

        for code in today_select.values:
            item = self.format_code(code)
            #新股不检测
            ms = re.findall(re.compile(r'\*|N|ST'), item['name'])
            if ms:
                continue

            #取一个按时间倒序排列
            _one_stock = self.df[self.df['s_code'] == item['s_code']].sort_values(by=('dateline'), ascending=False)
            print _one_stock
            if _one_stock.empty:
                continue
            '''
            $_first_top = $this->_get_prev_top($code,$today,$limit);
            $_first_low = $this->_get_prev_low($code,$_first_top,$_get_limit);
            $_today_low = $this->_get_prev_low($code,$today,$_get_limit);

            $res['one'] = $this->_sum_between_chg($_first_low,$_first_top,$code);
            $res['two'] = $this->_sum_between_chg($_today_low,$today,$code);

            '''
            #以今天为起点向左查找limit天里最近一个高点
            #select dateline,high,low from s_stock_trade where code='600836' and  dateline <=20151210 and now_top >30 order by high desc  limit 100);
            #比今天时间早
            _first_top_df = _one_stock[(_one_stock['dateline'] <= self.lastDay) & (_one_stock['high'] >= item['high'])].sort_values(by='high', ascending=False)
            #指定天数找不到前高 今天就是最近的高点 代表上涨趋势
            #print _first_top_df
            #print _first_top_df.iloc[0]
            #sys.exit()
            _first_top_day = self.format_code(_first_top_df.iloc[0])
            #今天创新查询时间段最高
            if item['dateline'] == _first_top_day['dateline']:
                print 'Today'

            print _first_top_day
            print "=========_first_top_day============"
            #sys.exit()

            #print _first_top_df
            #以今天和最高点之间查找最低一个低点
            #select dateline,high,low from s_stock_trade where  code='600836' and  dateline <=20151210  and now_low < ".$today['now_low']." order by dateline DESC  limit 10
            _nearest_low_df = _one_stock[(_one_stock['dateline'] < self.lastDay) & (_one_stock['dateline'] > _first_top_day['dateline']) & (_one_stock['low'] <= item['low'])].sort_values(by='low', ascending=True)
            #print _nearest_low_df
            #sys.exit()
            #
            #print _nearest_low_day
            #sys.exit()
            _nearest_low_day = []
            if _nearest_low_df.empty:
                if _first_top_day['dateline'] == item['dateline']:
                    print u'==========上涨趋势======='

                    if item['high'] > _first_top_day['high']:
                        print u'==========破前高======='
                    #查询离新高最近的一个低点
                    _nearest_low_df = _one_stock[(_one_stock['dateline'] < self.lastDay) & (_one_stock['low'] <= item['low'])].sort_values(by='low', ascending=True)
                    #print _nearest_low_df.iloc[0]
                    _nearest_low_day = self.format_code(_nearest_low_df.iloc[0])
                    #print item
                    right_up = ((item['high'] - _nearest_low_day['low'])/_nearest_low_day['low']) * 100
                    right_up = "{:,.2f}".format(right_up, ',')
                    #print right_up
                    #sys.exit()
                    #以最低点向左查找最近的一个高点,确认上一阶段的跌幅
                    _nearest_low_high_df = _one_stock[(_one_stock['dateline'] < _nearest_low_day['dateline']) & (_one_stock['high'] > _nearest_low_day['high'])].sort_values(by='high', ascending=False)
                    #print _nearest_low_high_df
                    #sys.exit()
                    if _nearest_low_high_df.empty:
                        #只有新股才会没有离最近低点的向左高点
                        pass
                    else:
                        _nearest_low_high_day = self.format_code(_nearest_low_high_df.iloc[0])
                        left_down = ((_nearest_low_high_day['high'] - _nearest_low_day['low'])/_nearest_low_high_day['high']) * 100
                        left_down = "{:,.2f}".format(left_down, ',')

                    #print left_down
                    #print right_up
                    #sys.exit()
                else:
                    print u'==========下跌趋势======='
                    #今天新低
                    _nearest_low_day = code
            else:
                _nearest_low_day = self.format_code(_nearest_low_df.iloc[0])
                #最高点到中间低的跌幅
                left_down = ((_first_top_day['high'] - _nearest_low_day['low'])/_first_top_day['high']) * 100
                left_down = "{:,.2f}".format(left_down, ',')
                #中间低点到今天的涨幅
                right_up = ((item['high'] - _nearest_low_day['low'])/_nearest_low_day['low']) * 100
                right_up = "{:,.2f}".format(right_up, ',')
                #print left_down
                #print right_up
                #print _nearest_low_day
                #sys.exit()
                #今天与高点之间有低点计算涨跌幅
                #pass
            #print _nearest_low_df
            #print _nearest_low_day
            #sys.exit()
            #以第一个高点为起点,向左查找最近的一个低点
            _first_top_prev_low_df = _one_stock[(_one_stock['dateline'] < _first_top_day['dateline']) & (_one_stock['low'] < _first_top_day['low'])].sort_values(by='low', ascending=True)
            print _first_top_prev_low_df.iloc[0]
            sys.exit()
