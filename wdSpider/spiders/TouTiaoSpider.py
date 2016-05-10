# -*- coding: utf-8 -*-
import sys
reload(sys)
import json
sys.setdefaultencoding("utf-8")
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.conf import settings
from wdSpider.utils.tools import sTools
from wdSpider.utils.db import sMysql
from wdSpider.items import WdspiderItem
import MySQLdb


class ZhihuSpider(BaseSpider):
    name = 'toutiao'
    allow_domains = ["toutiao.com"]
    #start_urls = ["http://zhidao.baidu.com/"]
    start_urls = ["http://toutiao.com/api/article/recent/?source=2&count=50&category=video&_=1462718705623"]
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
        return Request(url, callback=self.parse_list)

    def parse_list(self, response):
        self._get_page_parse(response)
        return False

    def _get_page_parse(self, response):
        _data = response.body
        re = json.loads(_data)
        mysql = sMysql('127.0.0.1', 'root', '1234asdf', 'quncms')
        for i in range(0, len(re['data'])):
            item = {}
            item['title'] = re['data'][i]['title']
            item['tag'] = re['data'][i]['tag']
            item['image_url'] = re['data'][i]['image_url']
            item['item_seo_url'] = re['data'][i]['item_seo_url']
            item['v_id'] = re['data'][i]['id']
            item['item_id'] = re['data'][i]['item_id']
            item['keywords'] = re['data'][i]['keywords']
            item['video_play_count'] = re['data'][i]['video_play_count']
            item['external_visit_count'] = re['data'][i]['external_visit_count']
            item['digg_count'] = re['data'][i]['digg_count']
            item['create_time'] = re['data'][i]['create_time']

            #item['title'] = "%s'xxxxxx" % item['title']

            #print MySQLdb.escape_string(item['title'])
            #sys.exit()
            _has = mysql.fetch_one("select * from  video_contents where item_id='%s'" % item['item_id'])
            #print item
            #
            if _has is None:
                mysql.dbInsert('video_contents', item)
            #sys.exit()
            #return 1
            vauthor = {}
            vauthor['media_name'] = re['data'][i]['media_name']
            vauthor['media_url'] = re['data'][i]['media_url']
            vauthor['middle_image'] = re['data'][i]['middle_image']

            _has = mysql.fetch_one("select * from video_author where media_url='%s'" % vauthor['media_url'])
            #print indata
            if _has is None:
                mysql.dbInsert('video_author', vauthor)
