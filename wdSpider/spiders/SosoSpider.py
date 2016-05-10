# -*- coding: utf-8 -*-
import random
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import urllib2
import urllib
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
#from scrapy.conf import settings
from wdSpider.utils.db import sMysql
import hashlib
from wdSpider.utils.tools import sTools
from wdSpider.items import WdspiderItem


class SosoSpider(BaseSpider):
    name = 'soso'
    allow_domains = ["soso.com"]
    #start_urls = ["http://zhidao.baidu.com/"]
    start_urls = [
        "http://wenwen.sogou.com/wapi/qun/world/list?groupUin=0&len=10&cateId=115&tagId=0&startPage=0&listType=&_=1461743864405",
        "http://wenwen.sogou.com/wapi/qun/world/list?groupUin=0&len=10&cateId=112&tagId=0&startPage=0&listType=&_=1461743864405",
        "http://wenwen.sogou.com/wapi/qun/world/list?groupUin=0&len=10&cateId=110&tagId=0&startPage=0&listType=&_=1461743864405",
        "http://wenwen.sogou.com/wapi/qun/world/list?groupUin=0&len=10&cateId=108&tagId=0&startPage=0&listType=&_=1461743864405",
        "http://wenwen.sogou.com/wapi/qun/world/list?groupUin=0&len=10&cateId=105&tagId=0&startPage=0&listType=&_=1461743864405",
        ]

    def __init__(self, category=None):
        super(BaseSpider, self).__init__()

    def make_requests_from_url(self, url):
        return Request(url, callback=self.parse_list)

    def __qun_wd(self, response):
        _data = response.body
        re = json.loads(_data)
        mysql = sMysql('127.0.0.1', 'root', '1234asdf', 'we_center')
        for i in range(0, len(re['qunWorldQuestionList'])):
            item = {}
            if re['qunWorldQuestionList'][i]['answerNum'] == 0:
                continue
            #print re['qunWorldQuestionList'][i].keys()
            #sys.exit()
            if 'answers' not in re['qunWorldQuestionList'][i].keys() or re['qunWorldQuestionList'][i]['answers'] is None:
                continue

            #print re['qunWorldQuestionList'][i]['answers']
            #sys.exit()
            item['question'] = re['qunWorldQuestionList'][i]['content'].encode('utf-8')
            item['question_detail'] = ''
            item['topics'] = ''
            item['answers'] = [{'agree_count': random.randint(5, 25), 'publish_time': time.time(), "comments": {}}]
            item['answers_text'] = re['qunWorldQuestionList'][i]['answers'][0]['richText'].encode('utf-8')
            item['signcc'] = 123123
            item['callback'] = 'http://wenwen.sogou.com/qun/world/question?qid=%s' % re['qunWorldQuestionList'][i]['id']


            _hash = hashlib.md5(item['callback']).hexdigest()
            _has = mysql.getRecord("select * from  spider_urls where hash='%s'" % _hash, 1)
            indata = {'url': item['callback'], 'hash': _hash}

            print indata
            if _has is None:
                mysql.dbInsert('spider_urls', indata)
            else:
                print "This Url exists....."
                continue
            req = urllib2.Request("http://www.zhidaode.com/?/shenjianshou/question/")
            data = urllib.urlencode(item)
            #enable cookie
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(req, data)
            print response.read()

    def parse_list(self, response):
        #hxs = HtmlXPathSelector(response)
        '''
        分页处理
        totalPage = hxs.select().extract()
        pagecount = 11
        for i in range(1,int(pagecount)):
            yield Request(response.url+"page"+str(i)+"/",callback=self.page_parse)

        '''
        self.__qun_wd(response)
        return False
        '''
        #print response.body
        stools = sTools()
        all_links = stools.sMatch('href="\/z\/q', '\.htm\?ch=wtk\.title">', response.body, 0)
        #all_links = hxs.select('//span[@clsss="fl"]/text()').extract()
        #print all_links
        #return
        for link in all_links:
            link = 'http://wenwen.sogou.com/z/q'+link+'.htm'
            items = {}
            if 'items' in response.meta.keys():
                items = response.meta["items"]

            yield Request(url=link, meta={"items": items}, callback=self.get_page_parse)
            #sys.exit()
        '''

    def get_page_parse(self, response):
        hxs = HtmlXPathSelector(response)
        item = WdspiderItem()
        _ans = hxs.xpath('//div[@class="answer-con"]/text()').extract()
        #print _ans
        if len(_ans[0]) < 30:
            print u"答案长度太短....."
            return None

        #sys.exit(),unicode(line,"UTF-8")"".join(_title)
        title = hxs.xpath('//h3[@id="questionTitle"]/text()').extract()
        '''
        _title = []
        for t in title[0]:
            _title.append(t.encode('utf-8'))
        '''
        item['question'] = title[0]
        item['question_detail'] = '',
        #item['topics'] = ,
        item['answers'] = [{'agree_count': random.randint(5, 25), 'publish_time': time.time(), "comments": {}}],
        item['answers_text'] = _ans[0]
        item['signcc'] = 123123,
        item['callback'] = response.url
        #print item
        return item
