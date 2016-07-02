# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import logging
import urllib
import MySQLdb
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
        if sys.argv[2] == '1':
            i = 0
            while 1:
                if i > 80:
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
                if status == 404 or status == 502:
                    mysql.dbQuery("DELETE FROM video_contents where itemid=%s" % data['itemid'])
                else:
                    html = self.sGet(url, 'utf-8')
                    #print html
                    tag = self.sMatch('tt-videoid="', '"', html, 0)
                    #print tag
                    #sys.exit()
                    if len(tag) == 0:
                        mysql.dbQuery("DELETE FROM video_contents where itemid=%s" % data['itemid'])
                    else:
                        up = {'video_id': tag[0], 'is_done': 1}
                        mysql.dbUpdate('video_contents', up, "itemid=%s" % data['itemid'])
        elif sys.argv[2] == '2':
            self.get_yy_show('dance', 11)

            self.get_yy_show('mc', 29)
        elif sys.argv[2] == '3':
            self.get_vlook_cate_list(1154)

    def get_vlook_cate_list(self, cate_id):
        url = "http://www.vlook.cn/ajx/n/square/category?cid=%s&scrollSpan=25&no=1&size=5&sid=3&rnd=0.2246547263694343" % cate_id
        html = self.sGet(url, 'utf-8')
        _data = json.loads(html)
        _data = _data['rst']['html']
        for i in range(0, len(_data)):
            if len(_data[i]) < 30:
                continue
            titles = self.sMatch('<font>', '<\/font>', _data[i], 0)
            print titles
            sys.exit()

    def get_yy_show(self, vtype, mid):
        self.tools.setup_logging(sys.argv[1], True, True)
        quncms_db = self.config['mysql']['quncms']
        mysql = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])
        for i in range(1, 10):

            url = 'http://www.yy.com/specialMore/page?biz=%s&subBiz=&moduleId=%s&page=%s' % (vtype, mid, i)
            print url
            html = self.sGet(url, 'utf-8')
            _data = json.loads(html)
            _data = _data['data']['data']
            for j in range(0, len(_data)):
                item = {
                    'yy_title': MySQLdb.escape_string(_data[j]['name']),
                    'yy_view': _data[j]['users'],
                    'yy_pic': _data[j]['thumb'],
                    'yy_id': _data[j]['sid'],
                }
                _has = mysql.fetch_one("select * from  video_yy where yy_id=%s" % item['yy_id'])
                if _has is None:
                    action = 'Add'
                    mysql.dbInsert('video_yy', item)
                else:
                    action = 'Update'
                    up = {'yy_title': item['yy_title'], 'yy_view': item['yy_view']}
                    mysql.dbUpdate('video_yy', up, "yy_id=%s" % item['yy_id'])

                logging.debug('%s=====:%s=====%s ' % (action, item['yy_title'], _data[j]['sid']))
            #sys.exit()

    def get_yy_red(self):
        self.tools.setup_logging(sys.argv[1], True, True)
        quncms_db = self.config['mysql']['quncms']
        mysql = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

        links = [
            'http://www.yy.com/t/red',
            #'http://www.yy.com/ent/dance',
            #'http://www.yy.com/ent/music'
        ]

        for i in range(0, len(links)):
            url = links[i]
            html = self.sGet(url, 'utf-8')
            titles = self.sMatch('<p class="video-title">', '<\/p>', html, 0)
            count = self.sMatch('<div class="audience-count">', '<\/div>', html, 0)
            pics = self.sMatch('data-original="', '"', html, 0)
            #3086431716
            gourl = self.sMatch('class="video-box" href="', '"', html, 0)

            for j in range(0, len(titles)):
                _vvid = gourl[j].split('_')
                if len(_vvid) < 2:
                    continue
                axd = self.tools.strip_tags(count[j])
                axd = axd.strip()
                item = {
                    'yy_title': MySQLdb.escape_string(titles[j]),
                    'yy_view': axd,
                    'yy_pic': pics[j],
                    'yy_id': _vvid[1],
                }

                _has = mysql.fetch_one("select * from  video_yy where yy_id=%s" % item['yy_id'])
                if _has is None:
                    action = 'Add'
                    mysql.dbInsert('video_yy', item)
                else:
                    action = 'Update'
                    up = {'yy_title': item['yy_title'], 'yy_view': item['yy_view']}
                    mysql.dbUpdate('video_yy', up, "yy_id=%s" % item['yy_id'])

                logging.debug('%s=====:%s=====%s ' % (action, item['yy_title'], gourl[j]))
