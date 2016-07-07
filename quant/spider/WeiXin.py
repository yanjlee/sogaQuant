# -*- coding: utf-8 -*-
import sys
import logging
import httplib
import hashlib
import pycurl
import cStringIO
#import time
import commands
import base64
import MySQLdb
#from bson.objectid import ObjectId
#from elasticsearch import Elasticsearch
#from bs4 import BeautifulSoup

from quant.core.Spider import *
UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"


class WeiXinSpider(SpiderEngine):
    '''
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        self.today = sys.argv[2]

    def get_info(self, vid):
        #self.get_from_news(url)
        self.get_wx_url(vid)

    def xget(self, url):
        buf = cStringIO.StringIO()

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 8)
        c.perform()
        #buf.close()
        return buf.getvalue()

    def xpost(self, url, jdata):
        jdata = json.dumps(jdata)
        req = urllib2.Request(url, jdata)

        response = urllib2.urlopen(req)
        print response.read()
        return response.read()

    def run(self):
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)
        #self.get_from_news(3, 'http://mp.weixin.qq.com/s?__biz=MzAwOTU3Nzc2MQ==&idx=6&mid=2650708612&sn=a52f461a2f8ccf664245cc5d9391a518')
        #sys.exit()

        '''
        url = "http://v.juhe.cn/weixin/redirect?wid=wechat_20160101000071"
        status = urllib.urlopen(url)
        print status.code
        print status.info()
        sys.exit()

        MONGO_IP = '127.0.0.1'
        client = pymongo.MongoClient(MONGO_IP, 27017)
        self.mango_db = client.spider

        self.es = Elasticsearch(host=ES_CONFIG['host'], port=ES_CONFIG['port'])
        '''
        quncms_db = self.config['mysql']['quncms']
        self.mysql2 = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

        if sys.argv[2] == '1':
            while not self.interrupted:
                #tmp = {'is_spider': 0}
                #record = self.mango_db.wx_juhe.find_one(tmp)
                record = self.mysql2.fetch_one("select * from wx_juhe where is_spider=0")
                if len(record) == 0:
                    break
                if record is not None:
                    self.get_from_news(record)

        elif sys.argv[2] == '2':
            i = 1
            while 1:
                if i > 10:
                    break
                record = self.mysql2.fetch_one("select * from wx_contents where is_post=0 and title != '' limit 1")
                self.xpost("http://www.uotee.com/ajax/post/", record)
                self.mysql2.dbQuery("update wx_contents set is_post=1 where id=%s" % record['id'])
                i += 1
                #sys.exit()
        else:
            vid = int(sys.argv[2])
            datas = []
            for i in range(1, 6):
                nvid = vid + i
                datas.append(nvid)

            vid += 5
            logging.debug('Done Vid=====:%s ' % vid)
            self.run_worker(datas)

    def get_wx_url(self, vid):

        conn = httplib.HTTPConnection("v.juhe.cn")
        conn.request('GET', "/weixin/redirect?wid=wechat_%s" % vid)
        l = ''
        for item in conn.getresponse().getheaders():
            if item[0] == 'location' and item[1] != '':
                l = item[1]
                break
        #if l == '':
        #    self.is_break += 1
        #else:
            #self.is_break = 0
        indata = {
            'dateline': self.tools.d_date('%Y%m%d'),
            'url_id': vid,
            'wx_url': l,
            'is_spider': 0
        }
        print indata
        #self.mango_db.wx_juhe.insert(indata) 85345
        self.mysql2.dbInsert('wx_juhe', indata)
        conn.close()

    def str_len(self, str):
        try:
            row_l = len(str)
            utf8_l = len(str.encode('utf-8'))
            return (utf8_l-row_l)/2+row_l
        except:
            return None
        return None

    def get_from_news(self, record):
        url = record['wx_url']
        #url = 'http://mp.weixin.qq.com/s?__biz=MzAxNzU1ODg2OQ==&idx=1&mid=403240725&sn=e4ecb34b0914946985db14dc341c4f82'
        pkid = record['id']
        out_put = '/usr/bin/php /htdocs/quant/c.php %s' % base64.b64encode(url)
        print out_put
        _data = commands.getoutput(out_put)
        #print record
        #sys.exit()
        if _data is False:
            return False
        _appuid = self.sMatch('appuin = "', '"\|\|"";', _data, 0)
        if len(_appuid) == 0:
            self.mysql2.dbQuery("delete from wx_juhe where id=%s" % pkid)
            #self.mango_db.wx_juhe.remove({'_id': ObjectId(record['_id'])})
            return False

        self.mysql2.dbQuery("update wx_juhe set is_spider=1 where id=%s" % pkid)
        #self.mango_db.wx_juhe.update({'_id': ObjectId(record['_id'])}, {'$set': {'is_spider': 1}})
        #sys.exit()
        _user_name = self.sMatch('user_name = "', '";', _data, 0)
        _nickname = self.sMatch('<strong class="profile_nickname">', "<\/strong>", _data, 0)
        _account = self.sMatch('<span class="profile_meta_value">', '<\/span>', _data, 0)
        _slogan = self.sMatch('<span class="profile_meta_value">', '<\/span>', _data, 0)

        _mid = self.sMatch('mid = "', '"', _data, 0)

        #_source = self.sMatch('source = "', '"', _data, 0)
        _sence = self.sMatch('scene = ', ';', _data, 0)
        _create_time = self.sMatch('ct = "', '"', _data, 0)
        #_ori_article_type = self.sMatch('_ori_article_type = "', '"', _data, 0)
        #_copyright_stat = self.sMatch('_copyright_stat = "', '"', _data, 0)
        _appmsg_type = self.sMatch('appmsg_type = "', '"', _data, 0)
        _msg_cdn_url = self.sMatch('msg_cdn_url = "', '"', _data, 0)
        _title = self.sMatch('<title>', '<\/title>', _data, 0)
        #_desc = self.sMatch('msg_desc = "', '"', _data, 0)
        _content = self.sMatch('<div class="rich_media_content " id="js_content">', '<\/div>', _data, 0)

        paurl = url.split('&')
        appuid = paurl[0].replace("http://mp.weixin.qq.com/s?__biz=", '')
        inuser = {
            'appuid': appuid,
            'mid': _mid[0],
            'user_name': _user_name[0],
            'user_account': _account[0],
            'nick_name': _nickname[0],
            'slogan': self.tools.strip_tags(_slogan[1])
        }
        print inuser
        #sys.exit()
        _has = self.mysql2.fetch_one("select * from  wx_open where appuid='%s'" % appuid)
        if _has is None:
            self.mysql2.dbInsert('wx_open', inuser)
        #return
        '''
        tmp = {'appuid': appuid}
        tmkp = self.mango_db.wx_open.find_one(tmp)
        #print record
        #sys.exit()
        if tmkp is None:
            #self.get_from_news(record)
            self.mango_db.wx_open.insert(inuser)
        #sys.exit()
        #appuid = _appuid[0]
        #_has = self.mysql.fetch_one("select * from  wx_open where appuid='%s'" % appuid)
        #if _has is None:
        #    axc = self.mysql.dbInsert('wx_open', inuser)
        #    appuid = axc['LAST_INSERT_ID()']
        '''
        #过滤文本内容太少的
        axd = self.tools.strip_tags(_content[0])
        axd = axd.strip()
        #print axd
        _l = self.str_len(axd.decode('utf-8'))

        if _l < 200:
            print "Length is ........."
            return False
        contxt = self.__clear_html(_content[0])
        title = self.__clear_html(_title[0])
        innews = {
            'appuid': appuid,
            'url': url,
            'title': MySQLdb.escape_string(title),
            'vdesc': '',
            'create_time': _create_time[0],
            #'source': _source[0],
            'sence': _sence[0],
            #'ori_article_type': _ori_article_type[0],
            #'copyright_stat': _copyright_stat[0],
            'appmsg_type': _appmsg_type[0],
            'msg_cdn_url': _msg_cdn_url[0],
            'content': MySQLdb.escape_string(contxt),
            'hash': hashlib.md5(url).hexdigest()
        }
        #self.es.index(index="wx_contents", doc_type='info', id=_hash, body=innews)
        #self.es.indices.refresh(index="wx_contents")
        #print innews
        #sys.exit()
        logging.debug('Done get_news=====:%s ' % innews['title'])
        self.mysql2.dbInsert('wx_contents_2', innews)
        return 1

    def __clear_html(self, htmlstr):
        htmlstr = htmlstr.replace('\r\n', '')
        htmlstr = htmlstr.replace("'", '')
        return htmlstr
