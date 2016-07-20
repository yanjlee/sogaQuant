# -*- coding: utf-8 -*-
import sys
import commands
import base64
from urllib import quote
from quant.core.Spider import *


class BaiduSpider(SpiderEngine):
    '''
    更新指数
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        quncms_db = self.config['mysql']['words']
        self.db2 = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])
        self.today = self.tools.d_date('%Y%m%d')

    def get_info(self, word):
        pass

    def run(self):
        self.tools.setup_logging(sys.argv[1], True, True)
        pass

    def get_word_pages(self):
        #50027
        i = int(sys.argv[2])
        self.tools.setup_logging(sys.argv[1], True, True)
        m = 100000
        while True:
            if i > m:
                break
            _has = self.db2.fetch_one("select * from  word_list where id='%s'" % i)
            i += 1
            print "TTTTTTTT===%s=" % i
            if _has is None:
                continue
            #_has['word'] = '有效吗'
            url = "http://www.baidu.com/s?wd=%s" % quote(_has['word'].replace(' ', '+'))
            #print url
            out_put = '/usr/bin/php /htdocs/quant/c.php %s' % base64.b64encode(url)
            html = commands.getoutput(out_put)
            nums = self.sMatch('百度为您找到相关结果约', '个', html, 0)
            print nums
            if len(nums) == 0:
                logging.debug("====NotFound Data=%s==" % i)
            else:
                nums = nums[0].replace(",", "")
                up = {'pages': int(nums)}
                self.db2.dbUpdate('word_list', up, "id=%s" % _has['id'])

            #拓展二级词
            th = self.sMatch('<th>', '<\/th>', html, 0)
            if len(th):
                for a in xrange(0, len(th)):
                    w = self.sMatch('<a href="(.*?)">', '<\/a>', th[a], 0)
                    print w
                    if len(w) == 0:
                        continue
                    second_w = w[0][1]
                    second_w = second_w.replace("\\", "")
                    second_w = second_w.replace("'", "")
                    #_hash = hashlib.md5(second_w).hexdigest()
                    #_has2 = self.db2.fetch_one("select * from  word_hash where hash_str='%s'" % _hash)
                    _hash_str = self.get_hash_key(second_w)
                    _has2 = self.db2.fetch_one("select * from  word_list where hash_str='%s'" % _hash_str[0])
                    if _has2 is None:
                        inwd = {
                            'dateline': self.today,
                            'hash_str': _hash_str[0],
                            'word': second_w,
                            'level': _has['level']+1
                        }
                        self.db2.dbInsert('word_list', inwd)
                    else:
                        up = {'dateline': self.today}
                        self.db2.dbUpdate('word_list', up, "id=%s" % _has2['id'])

            print "======================%s" % i

    def while_base_words_A(self):
        #base表 1274688
        #ALTER IGNORE TABLE word_list ADD UNIQUE INDEX(hash_str);
        '''
        i = 1
        m = 1274689
        while True:
            if i > m:
                break

            _has = self.db2.fetch_one("select * from  word_list where id='%s'" % i)
            i += 1
            if _has is None:
                continue
            print "=====%s===" % i
            _hash_str = self.get_hash_key(_has['word'])
            up = {'hash_str': _hash_str[0]}
            self.db2.dbUpdate('word_list', up, "id=%s" % _has['id'])
            #self.__get_bd_words(_has['name'])

        '''
        i = 1
        m = 3755
        while True:
            if i > m:
                break
            _has = self.db2.fetch_one("select * from  base where id='%s'" % i)
            i += 1
            if _has is None:
                continue
            print "=====%s===" % i
            self.__get_bd_words(_has['name'])

    def __get_bd_words(self, word):
        url = "https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd=%s&json=1&p=3req=2&csor=1&cb=j1&_=1466640657527" % word
        print url
        _data = self.sGet(url)
        _data = _data.replace("j1(", "")
        _data = _data.replace(");", "")
        _data = _data.replace("\\", "")
        _data = _data.replace("'", "")
        #print _data
        re = json.loads(_data)

        url2 = "http://nssug.baidu.com/su?wd=%s&prod=zhidao&_=1467750461243" % word
        _data2 = self.sGet(url2)
        #print _data
        _data2 = _data2.replace("window.baidu.sug(", "")
        _data2 = _data2.replace(");", "")
        _data2 = _data2.replace("\\", "")
        _data2 = _data2.replace("'", "")
        _data2 = _data2.replace("q:", '"q":')
        _data2 = _data2.replace("s:", '"s":')
        _data2 = _data2.replace("p:", '"p":')
        re2 = json.loads(_data2)
        #print re2['s']
        #sys.exit()
        c = []
        if len(re2['s']):
            c = re2['s']

        url3 = "http://nssug.baidu.com/su?wd=%s&prod=wenku&_=1467750461243" % word
        _data = self.sGet(url3)
        _data = _data.replace("window.baidu.sug(", "")
        _data = _data.replace(");", "")
        _data = _data.replace("\\", "")
        _data = _data.replace("'", "")
        _data = _data.replace("q:", '"q":')
        _data = _data.replace("s:", '"s":')
        _data = _data.replace("p:", '"p":')
        re3 = json.loads(_data)
        e = []
        if len(re3['s']):
            e = re3['s']

        b = []
        if 'g' in re.keys():
            for y in range(0, len(re['g'])):
                b.append(re['g'][y]['q'])
        a = []
        if len(re['s']):
            a = re['s']
        if len(a) or len(b) or len(c) or len(e):
            d = a + b + c + e
            d = list(set(d))
            #print d
            #sys.exit()
            for k in range(0, len(d)):
                #_hash = hashlib.md5(d[k]).hexdigest()
                _hash_str = self.get_hash_key(d[k])
                _has2 = self.db2.fetch_one("select * from  word_list where hash_str='%s'" % _hash_str[0])
                if _has2 is None:
                    #innews = {'hash_str': _hash}
                    #self.db2.dbInsert('word_hash', innews)
                    inwd = {
                        'hash_str': _hash_str[0],
                        'dateline': self.today,
                        'word': d[k],
                        'level': 1
                    }
                    self.db2.dbInsert('word_list', inwd)
                    daily_w = {
                        'dateline': self.today,
                        'word': d[k]
                    }
                    self.db2.dbInsert('daily_word', daily_w)
                else:
                    up = {'dateline': self.today}
                    self.db2.dbUpdate('word_list', up, "id=%s" % _has2['id'])

    def while_base_words(self):
        #keywords 表
        i = 1
        m = 157122
        while True:
            if i > m:
                break
            _has = self.db2.fetch_one("select * from  keywords where kid='%s'" % i)
            i += 1
            if _has is None:
                continue
            print "=====%s===" % i
            self.__get_bd_words(_has['keyword'])
