# -*- coding: utf-8 -*-
import sys
import logging
import json
import random
import datetime
import httplib
from quant.core.Spider import *


class TouTiaoSpider(SpiderEngine):
    '''
    分钟数据下载
    '''
    def __init__(self):
        SpiderEngine.__init__(self)
        quncms_db = self.config['mysql']['quncms']
        self.qundb = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

    def get_info(self, s_code):
        pass
        #self.get_minute_from_qq(s_code)
        #self.get_minute_from_sina(s_code)

    def run_list(self):
        #头条列表
        print sys.argv
        self.tools.setup_logging(sys.argv[1], True, True)
        _data = self.sGet('http://toutiao.com/api/article/recent/?source=2&count=50&category=video&_=1462718705623')
        re = json.loads(_data)
        #quncms_db = self.config['mysql']['quncms']
        #mysql = sMysql(quncms_db['host'], quncms_db['user'], quncms_db['password'], quncms_db['dbname'])

        for i in range(0, len(re['data'])):
            item = {}
            uid = re['data'][i]['media_url'].replace('http://toutiao.com/m', '')
            item['user_id'] = uid.replace('/', '')
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
            item['video_id'] = ''
            item['video_url'] = ''
            _has = self.qundb.fetch_one("select * from  video_contents where item_id='%s'" % item['item_id'])
            print item
            if _has is None:
                logging.debug('Done=====:%s=====%s ' % (item['title'], item['item_seo_url']))
                self.qundb.dbInsert('video_contents', item)

            vauthor = {}
            vauthor['media_name'] = re['data'][i]['media_name']
            vauthor['media_url'] = re['data'][i]['media_url']
            vauthor['middle_image'] = re['data'][i]['middle_image']

            _has = self.qundb.fetch_one("select * from video_author where media_url='%s'" % vauthor['media_url'])
            #print indata
            if _has is None:
                self.qundb.dbInsert('video_author', vauthor)

    def run_post(self):
        #定时发布一次80
        i = 0
        while 1:
            if i > 80:
                break
            data = self.qundb.fetch_one("select * from video_contents where is_done=0 and source_site=1")
            if data is None:
                break

            i += 1

            url = "http://www.toutiao.com%s" % data['item_seo_url']
            #
            print url
            logging.debug('===%s===url:%s' % (data['itemid'], url))
            status = urllib.urlopen(url).code
            if status == 404 or status == 502:
                self.qundb.dbQuery("DELETE FROM video_contents where itemid=%s" % data['itemid'])
            else:
                html = self.sGet(url, 'utf-8')
                #print html
                tag = self.sMatch('tt-videoid="', '"', html, 0)
                #print tag
                #sys.exit()
                if len(tag) == 0:
                    self.qundb.dbQuery("DELETE FROM video_contents where itemid=%s" % data['itemid'])
                else:
                    up = {'video_id': tag[0], 'is_done': 1}
                    self.qundb.dbUpdate('video_contents', up, "itemid=%s" % data['itemid'])

    def run_vlook(self):
        #微录
        self.__get_vlook_cate_list(1150)
        self.__get_vlook_cate_list(1151)
        self.__get_vlook_cate_list(1153)
        self.__get_vlook_cate_list(1154)
        self.__get_vlook_cate_list(1156)
        self.__get_vlook_cate_list(1157)
        self.__get_vlook_cate_list(1159)
        self.__get_vlook_cate_list(1160)
        self.__get_vlook_cate_list(1161)

        #发布
        self.run_vlook_post()

    def run_vlook_post(self):
        data = self.qundb.getRecord("select * from video_contents where is_done=0 and source_site=2")
        for i in range(0, len(data)):
            url = 'http://wtest.vlook.cn/show/qs/%s' % data[i]['video_id']
            _data = self.sGet(url, 'utf-8')
            #print _data
            params = self.sMatch("http:\/\/service.vlook.cn:8080", "'\);", _data, 0)
            conn = httplib.HTTPConnection("service.vlook.cn:8080")
            conn.request('GET', params[0])
            l = ''
            for item in conn.getresponse().getheaders():
                if item[0] == 'location' and item[1] != '':
                    l = item[1]
                    break
            if l:
                up = {'video_url': l, 'is_done': 1}
                self.qundb.dbUpdate('video_contents', up, "itemid=%s" % data[i]['itemid'])

    def __get_vlook_cate_list(self, cate_id):
        caate = {
            '1150': 'video_child',
            '1151': 'video_pet',
            '1153': 'video_hongren',
            '1154': 'video_meinv',
            '1156': 'video_funny',
            '1157': 'video_travel',
            '1159': 'video_sports',
            '1160': 'video_food',
            '1161': 'video_movie'
        }
        url = "http://www.vlook.cn/ajx/n/square/category?cid=%s&scrollSpan=25&no=1&size=50&sid=3&rnd=0.2246547263694343" % cate_id
        html = self.sGet(url, 'utf-8')
        _data = json.loads(html)
        _data = _data['rst']['html']
        for i in range(0, len(_data)):
            if len(_data[i]) < 30:
                continue
            titles = self.sMatch('<font>', '<\/font>', _data[i], 0)
            username = self.sMatch('<span title="(.*?)">', '<\/span>', _data[i], 0)
            video_id = self.sMatch('<a href="\/show\/qs\/', '"', _data[i], 0)
            blogid = self.sMatch('<a href="\/ta\/qs\/', '"', _data[i], 0)
            blogid = "http://www.vlook.cn/ta/qs/%s" % blogid[0]
            dateline = self.sMatch('<span class="font1" title="', '">', _data[i], 0)
            srcs = self.sMatch('src="', '"', _data[i], 0)
            d = datetime.datetime.strptime(dateline[0], "%Y-%m-%d %H:%M:%S")
            ctime = time.mktime(d.timetuple())

            uid = self.sMatch('blogId="', '"', _data[i], 0)
            #sys.exit()
            axd = self.tools.strip_tags(titles[0])
            item = {}
            item['vlook_uid'] = uid[0]
            item['source_site'] = 2
            item['user_id'] = 0
            item['title'] = axd
            item['tag'] = caate[str(cate_id)]
            item['image_url'] = srcs[1]
            item['item_seo_url'] = ''
            item['v_id'] = 0
            item['item_id'] = 0
            item['keywords'] = ''
            item['video_play_count'] = random.randint(10, 2000)
            item['external_visit_count'] = random.randint(10, 100)
            item['digg_count'] = random.randint(10, 100)
            item['create_time'] = str(ctime)
            item['video_id'] = video_id[0]
            item['video_url'] = ''
            #item['is_done'] = 1
            _has = self.qundb.fetch_one("select * from  video_contents where video_id='%s'" % item['video_id'])
            #print _has
            #sys.exit()
            if _has is None:
                logging.debug('Done=====:%s=====%s ' % (item['title'], item['video_id']))
                self.qundb.dbInsert('video_contents', item)

            vauthor = {}
            vauthor['media_name'] = username[0][0]
            vauthor['media_url'] = "%s|%s" % (uid[0], str(blogid))
            vauthor['middle_image'] = srcs[0]
            #print vauthor
            _has = self.qundb.fetch_one("select * from video_author where media_url='%s'" % vauthor['media_url'])
            if _has is None:
                self.qundb.dbInsert('video_author', vauthor)

    def run_yy(self):
        #yy直播
        self.__get_yy_show('dance', 11)

        self.__get_yy_show('mc', 29)

    def __get_yy_show(self, vtype, mid):
        self.tools.setup_logging(sys.argv[1], True, True)
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
                _has = self.qundb.fetch_one("select * from  video_yy where yy_id=%s" % item['yy_id'])
                if _has is None:
                    action = 'Add'
                    self.qundb.dbInsert('video_yy', item)
                else:
                    action = 'Update'
                    up = {'yy_title': item['yy_title'], 'yy_view': item['yy_view']}
                    self.qundb.dbUpdate('video_yy', up, "yy_id=%s" % item['yy_id'])

                logging.debug('%s=====:%s=====%s ' % (action, item['yy_title'], _data[j]['sid']))

    def __get_yy_red(self):
        #红人,不用直播不固定
        self.tools.setup_logging(sys.argv[1], True, True)
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

                _has = self.qundb.fetch_one("select * from  video_yy where yy_id=%s" % item['yy_id'])
                if _has is None:
                    action = 'Add'
                    self.qundb.dbInsert('video_yy', item)
                else:
                    action = 'Update'
                    up = {'yy_title': item['yy_title'], 'yy_view': item['yy_view']}
                    self.qundb.dbUpdate('video_yy', up, "yy_id=%s" % item['yy_id'])

                logging.debug('%s=====:%s=====%s ' % (action, item['yy_title'], gourl[j]))
