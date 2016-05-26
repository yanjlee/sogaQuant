# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import logging
import urllib
import base64
from quant.core.Spider import *
from quant.core.Spider import *
UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"


class TouTiaoDetailSpider(SpiderEngine):

    def __init__(self):
        SpiderEngine.__init__(self)

    def get_info(self, vid):
        pass
        #self.get_from_news(url)
        #self.get_wx_url(vid)

    def run(self):
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)
        quncms_db = self.config['mysql']['quncms']
        mysql = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])
        i = 0
        while 1:
            if i > 50:
                break
            data = mysql.fetch_one("select * from video_contents where is_done=0")
            if data is None:
                break

            i += 1

            url = "http://www.toutiao.com%s" % data['item_seo_url']
            #
            print url
            logging.debug('===%s===url:%s' % (data['itemid'], url))
            status = urllib.urlopen(url).code
            if status == 404:
                mysql.dbQuery("DELETE FROM video_contents where itemid=%s" % data['itemid'])
            else:
                html = self.sGet(url, 'utf-8')
                #print html
                tag = self.sMatch('tt-videoid="', '"', html, 0)
                print tag
                if len(tag) == 0:
                    up = {'is_done': 1}
                else:
                    up = {'video_id': tag[0]}
                    urlcode = "http://i.snssdk.com/video/urls/1/toutiao/mp4/%s" % tag[0]
                    urldata = self.sGet(urlcode, 'utf-8')
                    jdata = json.loads(urldata)

                    c = jdata['data']['video_list']
                    print c
                    curl = ''
                    if 'video_3' in c.keys():
                        curl = c['video_3']['main_url']
                    elif 'video_2' in c.keys():
                        curl = c['video_2']['main_url']
                    elif 'video_1' in c.keys():
                        curl = c['video_1']['main_url']

                    curl = curl.replace("\n", "@@@")
                    url = "http://video.155027.com/content/code/?c=%s&id=%s" % (base64.b64encode(curl), data['itemid'])
                    print url
                    html = self.sGet(url, 'utf-8')
                    #print html
                    #sys.exit()
                mysql.dbUpdate('video_contents', up, "itemid=%s" % data['itemid'])
