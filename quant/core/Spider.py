#! -*- coding:utf-8 -*-
import os
import urllib2
import re
from quant.core.Worker import *
from quant.core.Abstract import *
WORKER = 8


class SpiderEngine(Abstract):
    ref = ''

    #def __init__(self):
        #self.mysql = sMysql(MYSQL_DB['host'], MYSQL_DB['user'], MYSQL_DB['password'], MYSQL_DB['dbname'])
        #self.headers = []

    def run_worker(self, data):
        requests = makeRequests(self.get_info, data, self.print_result, self.handle_exception)
        print ("Creating thread pool with %s worker threads." % WORKER)
        main = ThreadPool(WORKER)
        for req in requests:
            main.putRequest(req)
            print ("Work request #%s added." % req.requestID)
        main.wait()

    def run_php_worker(self, data):
        requests = makeRequests(self.run_shell, data, self.print_result, self.handle_exception)
        print ("Creating thread pool with %s worker threads." % WORKER)
        main = ThreadPool(WORKER)
        for req in requests:
            main.putRequest(req)
            print ("Work request #%s added." % req.requestID)
        main.wait()

    def get_info(self, kparam):
        pass

    def run_shell(self, kparam):
        os.system(kparam)
        return True

    def set_headers(self, h):
        if h not in self.headers:
            self.headers.append(h)

    def get_headers(self):
        return self.headers

    def set_refer(self, ref):
        self.ref = ref

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
        if self.ref is not None:
            headers['Referer'] = self.ref
        import cookielib
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        urllib2.install_opener(opener)
        #print url
        req = urllib2.Request(url=url, headers=headers)

        try:
            data = urllib2.urlopen(req)
        except:
            data = urllib2.urlopen(req)
        #print data
        #sys.exit()
        data = data.read()
        #print data
        #sys.exit()
        if ch == 'gbk':
            data = data.decode("gbk", 'ignore')
        elif ch == 'utf8':
            data = data.decode("utf-8")
        return data

    def sPost(self, url, postdata={}, cookies={}, ch='gbk', bt='solomon'):
        bots = {"baidu": "Baiduspider+(+http://www.baidu.com/search/spider.htm)", 'google': "Googlebot/2.1 (+http://www.google.com/bot.html)", 'solomon': "Solomon Net Vampire/1.0"}
        headers = {'User-Agent': bots[bt]}
        values = urllib.parse.urlencode(postdata)
        req = urllib.request.Request(url, values, headers)
        data = urllib.request.urlopen(req)
        data = data.read()
        if ch == 'gbk':
            data = data.decode("gbk", 'ignore')
        return data

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

    def sTags(self, htmlstr):
        htmlstr = re.sub(r'<script[^>]*?>.*?</script>', '', htmlstr)
        htmlstr = re.sub(r'<style[^>]*?>.*?</style>', '', htmlstr)
        htmlstr = re.sub(r'<!--.*?-->', '', htmlstr)
        htmlstr = re.sub(r'<[\/\!]*?[^<>]*?>', '', htmlstr)
        htmlstr = re.sub(r'/\**?\*/', '', htmlstr)
        htmlstr = re.sub(r'</?\w+[^>]*>', '', htmlstr)
        htmlstr = re.sub(r'([\r\n])[\s]+', '', htmlstr)
        #先过滤CDATA
        #htmlstr=re.sub(r'//<!\[CDATA\[[^>]*//\]\]>','',htmlstr) #匹配CDATA
        #htmlstr=re.sub(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>','',htmlstr)#Script
        #htmlstr=re.sub(r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>','',htmlstr)#style
        #htmlstr=re.sub(r'<br\s*?/?>','',htmlstr)#处理换行
        #htmlstr=re.sub(r'</?\w+[^>]*>','',htmlstr)#HTML标签
        #htmlstr=re.sub(r'<!--[^>]*-->','',htmlstr)#HTML注释
        #htmlstr = re.sub(r'([\r\n])[\s]+','',htmlstr)
        #s=re_cdata.sub('',htmlstr)#去掉CDATA
        #s=re_script.sub('',s) #去掉SCRIPT
        #s=re_style.sub('',s)#去掉style
        #s=re_br.sub('\n',s)#将br转换为换行
        #s=re_h.sub('',s) #去掉HTML 标签
        #s=re_comment.sub('',s)#去掉HTML注释
        #去掉多余的空行
        #blank_line=re.compile('\n+')
        #s=blank_line.sub('\n',s)
        #s=replaceCharEntity(s)#替换实体
        return htmlstr

    def print_result(self, request, result):
        print request
        print ("**** Result from request #%s: %r" % (request.requestID, result))

    #异常处理
    def handle_exception(self, request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print (request)
            print (exc_info)
            raise SystemExit
        print ("**** Exception occured in request #%s: %s" % (request.requestID, exc_info))
