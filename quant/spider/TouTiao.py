# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import logging
import json
from quant.core.Spider import *


class TouTiaoSpider(SpiderEngine):
    '''
    分钟数据下载
    '''
    def __init__(self):
        SpiderEngine.__init__(self)

    def get_info(self, s_code):
        pass
        #self.get_minute_from_qq(s_code)
        #self.get_minute_from_sina(s_code)

    def run(self):
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)
        _data = self.sGet('http://toutiao.com/api/article/recent/?source=2&count=50&category=video&_=1462718705623')
        re = json.loads(_data)
        quncms_db = self.config['mysql']['quncms']
        mysql = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

        for i in range(0, len(re['data'])):
            item = {}
            item['title'] = re['data'][i]['title']
            item['tag'] = re['data'][i]['tag']
            item['image_url'] = re['data'][i]['image_url']
            item['item_seo_url'] = re['data'][i]['item_seo_url']
            item['v_id'] = str(re['data'][i]['id'])
            item['item_id'] = str(re['data'][i]['item_id'])
            item['keywords'] = str(re['data'][i]['keywords'])
            item['video_play_count'] = str(re['data'][i]['video_play_count'])
            item['external_visit_count'] = str(re['data'][i]['external_visit_count'])
            item['digg_count'] = str(re['data'][i]['digg_count'])
            item['create_time'] = str(re['data'][i]['create_time'])

            _has = mysql.fetch_one("select * from  video_contents where item_id='%s'" % item['item_id'])
            print item
            if _has is None:
                logging.debug('Done=====:%s=====%s ' % (item['title'], item['item_seo_url']))
                mysql.dbInsert('video_contents', item)

            vauthor = {}
            vauthor['media_name'] = re['data'][i]['media_name']
            vauthor['media_url'] = re['data'][i]['media_url']
            vauthor['middle_image'] = re['data'][i]['middle_image']

            _has = mysql.fetch_one("select * from video_author where media_url='%s'" % vauthor['media_url'])
            #print indata
            if _has is None:
                mysql.dbInsert('video_author', vauthor)
