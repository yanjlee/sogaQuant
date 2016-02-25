# -*- coding: UTF-8 -*-

'''
a = sTools()
staticmethod调用不用实例化 sTools.func()
'''
#import urllib.parse,
import re
import time
from datetime import *
'''
__all__ = [
    'sWrite',
    'sGet',
    'sPost',
    'sMatch',
    'sTags'
    'one_stringhash'
]
'''
DOT = frozenset('.')


class sTools:

    def __init__(self):
        pass

    def __call__(self):
        pass

    def get_current_year(self):
        return time.localtime(time.time())[0]

    def is_alpha_chn(self, content_str):
        for uchar in content_str:
            if not re.match(ur'[\.0-9·《》\sA-z\u4e00-\u9fa5]+', uchar) and not re.match(ur'[^<>:]+', uchar):
                return False
        return True

    def is_alphabet(self, uchar):
        """判断一个unicode是否是英文字母"""
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False

    def is_chinese(self, uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False

    def val(self, val):
        if val is None:
            return None
        if val == 'null':
            return None
        if val == 'undefined':
            return None
        if val == 0:
            return val
        if val == []:
            return None
        if val == {}:
            return None
        if isinstance(val, basestring) and len(val) == 0:
            return None
        if isinstance(val, dict) and len(val) == 0:
            return None
        return val

    def debug(self, xlist):
        l = len(xlist)
        for i in range(0, l):
            print "===".join(xlist[i])

    #格式化Money为千分位
    def format_money(self, m):
        return "{:,.2f}".format(m, ',')

    #格式化日期
    def d_date(self, ymd='%Y-%m-%d %H:%M:%S', unix_time=0):
        if unix_time == 0:
            unix_time = datetime.now().strftime("%s")

        unix_time = int(unix_time)
        return datetime.fromtimestamp(unix_time).strftime(ymd)

    def sWrite(self, text, filename='log.txt'):
        fp = open(filename, 'a+')
        #text = self.d_date() + " == " + text + "\n"
        output = " %s == %s \n" % (self.d_date(), text)
        fp.write(output)

    _benchmark = {}

    def benchmark_begin(self, name):
        self._benchmark[name] = {'b': datetime.now().strftime("%s"), 'b2': datetime.now().microsecond}

    def benchmark_end(self, name):
        if name in self._benchmark:
            self._benchmark[name].update({'e': datetime.now().strftime("%s"), 'e2': datetime.now().microsecond})
        else:
            self._benchmark[name] = {'e': datetime.now().strftime("%s"), 'e2': datetime.now().microsecond}
