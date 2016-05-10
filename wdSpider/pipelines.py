# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import time
import sys
import urllib
import urllib2
from wdSpider.utils.tools import sTools
from scrapy.conf import settings
from wdSpider.utils.db import sMysql
import hashlib


class WdspiderPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        self.start_time = time.time()
        #self.count +=1

    def close_spider(self, spider):
        #print "All Done ! Collect:%s, All_duration:%s"+(self.count,time.time()-self.start_time);
        print "All Done"

    def after_post(self):
        pass

    def process_item(self, item, spider):

        if "WdspiderItem" in item.__class__.__name__:
            stools = sTools()
            mysql = sMysql('127.0.0.1', 'root', '1234asdf', 'we_center')
            _hash = hashlib.md5(item['callback']).hexdigest()
            _has = mysql.getRecord("select * from  spider_urls where hash='%s'" % _hash, 1)
            indata = {'url': item['callback'], 'hash': _hash}

            print indata
            if _has is None:
                mysql.dbInsert('spider_urls', indata)
            else:
                print "This Url exists....."
                return False

            url2 = 'http://hint.wenwen.sogou.com/web?ie=utf8&callback=hintdata&query=%s&jsonpCallback=hintdata&_=0.797329780370241&callback=hintdata' % item['question']
            print url2
            _data2 = stools.sGet(url2, 'utf8')

            _topic = _data2.replace('hintdata([', '')
            _topic = _topic.replace('])', '')
            _topic = _topic.replace('"', '')
            item['topics'] = _topic
            item['question_detail'] = ''
            #print item

            req = urllib2.Request(settings['SEND_URL'])
            data = urllib.urlencode(item)
            #enable cookie
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(req, data)
            return response.read()
