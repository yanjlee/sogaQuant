# -*- coding: utf-8 -*-
import random
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import TextResponse, Request
from scrapy.conf import settings
from wdSpider.utils.tools import sTools

import wdSpider
from wdSpider.items import WdspiderItem


class ZhihuSpider(BaseSpider):
    name = 'zhihu'
    allow_domains = ["zhihu.com"]
    #start_urls = ["http://zhidao.baidu.com/"]
    start_urls = [
        "http://www.zhihu.com/explore",
        #u"http://www.zhihu.com/search?type=content&q=女主播不许吃香蕉"
        ]
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "http://www.zhihu.com/"
    }

    def __init__(self, category=None):
        super(BaseSpider, self).__init__()

    def make_requests_from_url(self, url):
        return Request(url, callback=self.parse_list, headers=self.headers)

    def parse_list(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        分页处理
        totalPage = hxs.select().extract()
        pagecount = 11
        for i in range(1,int(pagecount)):
            yield Request(response.url+"page"+str(i)+"/",callback=self.page_parse)

        '''
        all_links = hxs.select('//a[@class="question_link"]/@href').extract()
        #all_links = hxs.select('//a[@class="js-title-link"]/@href').extract()

        #print all_links
        #sys.exit()
        for link in all_links:
            link = 'http://www.zhihu.com'+link
            items = {}
            if 'items' in response.meta.keys():
                items = response.meta["items"]

            yield Request(url=link, meta={"items": items}, callback=self.get_page_parse, headers=self.headers)

    def get_page_parse(self, response):
        hxs = HtmlXPathSelector(response)
        item = WdspiderItem()

        title = hxs.select('//title/text()').extract()

        ask_list = hxs.select('//div[@class="zm-editable-content clearfix"]/text()').extract()
        askstr = ''
        if len(ask_list) > 0:
            for ask in ask_list:
                ask = ask.encode('utf-8')
                askstr += ask+"<br>"
        st = sTools()
        _title = title[0].encode('utf-8').replace(u'- 知乎', '')
        _title = _title.replace("\n", '')
        item['question'] = st.strip_tags(_title)
        item['question_detail'] = ''
        item['answers'] = [{'agree_count': random.randint(5, 25), 'publish_time': time.time(), "comments": {}}]
        item['answers_text'] = askstr
        item['signcc'] = 123123
        item['callback'] = response.url
        #print item
        return item
