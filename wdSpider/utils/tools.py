# -*- coding: UTF-8 -*-

'''
a = sTools()
staticmethod调用不用实例化 sTools.func()
'''
#import urllib.parse,
import re
import os
import time
import logging
import logging.handlers
from datetime import *
import urllib2
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

    def sMatch(self, start, end, text, isformat=1):
        pattern = '%s(.*?)%s' % (start, end)
        ms = re.compile(pattern, re.S)
        #去除html标签
        if isformat == 1:
            text = re.sub(r'<script[^>]*?>.*?</script>', '', text)
            text = re.sub(r'<style[^>]*?>.*?</style>', '', text)
            text = re.sub(r'<!--.*?-->', '', text)
            text = re.sub(r'<[\/\!]*?[^<>]*?>', '', text)
            text = re.sub(r'/\**?\*/', '', text)
            text = re.sub(r'([\r\n])[\s]+', '', text)
        #print(text);
        return ms.findall(text)

    def sGet(self, url, ch='gbk', bt='solomon'):
        bots = {
            "baidu": "Baiduspider+(+http://www.baidu.com/search/spider.htm)",
            'google': "Googlebot/2.1 (+http://www.google.com/bot.html)",
            'solomon': "Solomon Net Vampire/1.0",
            'de': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:44.0) Gecko/20100101 Firefox/44.0"
        }
        headers = {
            #'Host': 'www.super-ping.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'User-Agent': bots[bt],
            #'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
        }
        import cookielib
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        urllib2.install_opener(opener)
        req = urllib2.Request(url=url, headers=headers)

        try:
            data = urllib2.urlopen(req)
        except IOError, e:
            print e

        data = data.read()
        if ch == 'gbk':
            data = data.decode("gbk", 'ignore')
        elif ch == 'utf8':
            data = data.decode("utf-8")
        return data

    def setup_logging(self, job, daemon=False, verbose=False):
        #log_folder = '%s/%s' % (JOB_LOGS_DIRECTORY, job)
        #file_path = '%s/%s' % (MIN_DATA_LOG, self.today)
        if os.path.exists(JOB_LOGS_DIRECTORY) is False:
            os.makedirs(JOB_LOGS_DIRECTORY)

        log_filename = '%s/%s.log' % (JOB_LOGS_DIRECTORY, job)
        logger = logging.getLogger()

        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        handlers = []

        if daemon:
            handlers.append(logging.handlers.TimedRotatingFileHandler(filename=log_filename, when='midnight'))
        else:
            handlers.append(logging.FileHandler(filename='%s.%s' % (log_filename, time.strftime('%Y-%m-%d'))))

        handlers.append(logging.StreamHandler())

        for handler in handlers:
            if verbose:
                handler.setLevel(logging.DEBUG)
            else:
                handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)

    def strip_tags(self, string, allowed_tags=''):
        if allowed_tags != '':
            # Get a list of all allowed tag names.
            allowed_tags_list = re.sub(r'[\/<> ]+', '', allowed_tags).split(',')
            allowed_pattern = ''
            for s in allowed_tags_list:
                if s == '':
                    continue
                    # Add all possible patterns for this tag to the regex.
                    if allowed_pattern != '':
                        allowed_pattern += '|'
                        allowed_pattern += '<' + s + ' [^><]*>$|<' + s + '>|'
                     # Get all tags included in the string.
            all_tags = re.findall(r'<]+>', string, re.I)
            for tag in all_tags:
                # If not allowed, replace it.
                if not re.match(allowed_pattern, tag, re.I):
                    string = string.replace(tag, '')
        else:
            # If no allowed tags, remove all.
            string = re.sub(r'<[^>]*?>', '', string)
        return string
