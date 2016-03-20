# -*- coding: utf-8 -*-
from quant.core.Stats import *


class TdxAnalyse(StatsEngine):

    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    '''
    Tdx分时异动
    '''
    def filter_code(self, codeName):
        ms = re.findall(re.compile(r'\*|N|ST'), codeName)
        return ms

    def run(self, fromfile, tofile):
        print self.args
        data = {}
        f = open(fromfile, 'rb')
        lines = f.readlines()
        for line in lines:
            line = line.decode('gbk', 'ignore').encode('utf8')
            #line = '10:06\t海南板块(880230)\t撑杆跳高\t1.08%'
            _tmp = line.split("\t")
            _cinfo = _tmp[1].split("(")
            code = _cinfo[1].replace(')', '')

            if code[0:1] == '8' or code[0:1] == '9':
                continue
            code = self.__co_scode(code)
            if code not in data.keys():
                data[code] = {
                    's_code': code,
                    'name': _cinfo[0],
                    'up': 0,
                    'down': 0,
                    'rebound': 0,
                    'rebound_no': 0,
                    'jump': 0,
                    'jump_no': 0,
                    'bigUp': 0,
                    #'bigUp_no': 0,
                    'bigDown': 0,
                    #'bigDown_no': 0,
                    'B': 0,
                    'B_no': 0,
                    'S': 0,
                    'S_no': 0,
                    'BS': 0,

                    'mai': 0,
                    'mai_no': 0,
                    'chemai': 0,
                    'chemai_no': 0
                }
            c = _tmp[2].strip()
            #print c.strip()
            #sys.exit()
            d = _tmp[3].strip()
            d = d.replace("％", "")
            dt = d.split("/")

            if c == '拖拉机买(L2)':
                continue
            elif c == '拖拉机卖(L2)':
                continue
            elif c == '挂买异动(L2)':
                data[code]['mai'] += int(dt[1])
                data[code]['mai'] += 1
            elif c == '撤买异动(L2)':
                data[code]['chemai'] += int(dt[1])
                data[code]['chemai_no'] += 1
            elif c == '挂卖异动(L2)':
                continue
            elif c == '撤卖异动(L2)':
                continue
            elif c == '主力买入':
                data[code]['B'] += int(dt[1])
                data[code]['B_no'] += 1
            elif c == '主力卖出':
                data[code]['S'] += int(dt[1])
                data[code]['S_no'] += 1
            elif c == '加速拉升':
                data[code]['up'] += float(d)
            elif c == '加速下跌':
                data[code]['down'] += float(d)
            elif c == '低位反弹':
                data[code]['rebound'] += float(d)
                data[code]['rebound_no'] += 1
            elif c == '高位回落':
                continue
            elif c == '撑杆跳高':
                data[code]['jump'] += float(d)
                data[code]['jump_no'] += 1
            elif c == '平台跳水':
                continue
            elif c == '单笔冲涨':
                data[code]['bigUp'] += float(d)
            elif c == '单笔冲跌':
                data[code]['bigDown'] += float(d)
            elif c == '区间放量(跌)':
                continue
            elif c == '区间放量(涨)':
                continue
            elif c == '区间放量':
                continue

        #print data['sz600673']
        #sys.exit()
        f = "代码,名称,拉升值,下跌值,反弹值,反弹次数,撑高值,撑高次数,单涨,单跌,主力买入,主力买次数,主力卖,主力卖次数,买卖对比,挂买汇总,挂买次数,撤买汇总,撤买次数\n"
        for s_code in data.keys():
            if data[s_code]['up'] == 0 and data[s_code]['down'] == 0 and data[s_code]['rebound'] == 0 and data[s_code]['jump'] == 0 and data[s_code]['B'] == 0 and data[s_code]['S'] == 0:
                continue
            if data[s_code]['down'] > 2:
                continue
            ms = self.filter_code(data[s_code]['name'])
            if ms:
                continue
            #大盘股
            if data[s_code]['up'] == 0 and data[s_code]['mai'] > 100000:
                continue

            if data[s_code]['up'] == 0 and data[s_code]['rebound'] == 0 and data[s_code]['B'] == 0:
                continue

            if data[s_code]['B'] > 0 or data[s_code]['S'] > 0:
                if data[s_code]['B'] == 0:
                    data[s_code]['BS'] = -1
                elif data[s_code]['S'] == 0:
                    data[s_code]['BS'] = 99
                else:
                    right_up = data[s_code]['B']/data[s_code]['S']
                    data[s_code]['BS'] = float('%2f' % right_up)

            stx = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                str(data[s_code]['s_code']),
                str(data[s_code]['name']),
                str(data[s_code]['up']),
                str(data[s_code]['down']),
                str(data[s_code]['rebound']),
                str(data[s_code]['rebound_no']),
                str(data[s_code]['jump']),
                str(data[s_code]['jump_no']),
                str(data[s_code]['bigUp']),
                str(data[s_code]['bigDown']),
                str(data[s_code]['B']),
                str(data[s_code]['B_no']),
                str(data[s_code]['S']),
                str(data[s_code]['S_no']),
                str(data[s_code]['BS']),
                str(data[s_code]['mai']),
                str(data[s_code]['mai_no']),
                str(data[s_code]['chemai']),
                data[s_code]['chemai_no']
                )
            fp = open(tofile, 'a+')
            fp.write(stx)

    def __co_scode(self, code):
        a = code[0:1]
        b = ''
        if a == 6:
            b = 'sh%s'
        else:
            b = 'sz%s'
        return b % code
