# -*- coding: utf-8 -*-
'''

'''
import sys
import json
import math
import MySQLdb
from quant.core.Spider import *

# file extensions
mediatype = [
    ".wma", ".wav", ".mp3", ".aac", ".ra", ".ram", ".mp2", ".ogg", \
    ".aif", ".mpega", ".amr", ".mid", ".midi", ".m4a", ".m4v", ".wmv", \
    ".rmvb", ".mpeg4", ".mpeg2", ".flv", ".avi", ".3gp", ".mpga", ".qt", \
    ".rm", ".wmz", ".wmd", ".wvx", ".wmx", ".wm", ".swf", ".mpg", ".mp4", \
    ".mkv", ".mpeg", ".mov", ".mdf", ".iso", ".asf", ".vob"
]
imagetype = [
    ".jpg", ".jpeg", ".gif", ".bmp", ".png", ".jpe", ".cur", ".svg", \
    ".svgz", ".tif", ".tiff", ".ico"
]
doctype = [
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".vsd", ".txt", ".pdf", \
    ".ods", ".ots", ".odt", ".rtf", ".dot", ".dotx", ".odm", ".pps", ".pot", \
    ".xlt", ".xltx", ".csv", ".ppsx", ".potx", ".epub", ".apk", ".exe", \
    ".msi", ".ipa", ".torrent", ".mobi"
]
archivetype = [
    ".7z", ".a", ".ace", ".afa", ".alz", ".android", ".apk", ".ar", \
    ".arc", ".arj", ".b1", ".b1", ".ba", ".bh", ".bz2", ".cab", ".cab", \
    ".cfs", ".chm", ".cpio", ".cpt", ".cqm", ".dar", ".dd", ".dgc", ".dmg", \
    ".ear", ".ecc", ".eqe", ".exe", ".f", ".gca", ".gz", ".ha", ".hki", \
    ".html", ".ice", ".id", ".infl", ".iso", ".jar", ".kgb", ".lbr", \
    ".lha", ".lqr", ".lz", ".lzh", ".lzma", ".lzo", ".lzx", ".mar", ".ms", \
    ".net", ".package", ".pak", ".paq6", ".paq7", ".paq8", ".par", ".par2", \
    ".partimg", ".pea", ".pim", ".pit", ".qda", ".rar", ".rk", ".rz", \
    ".s7z", ".sda", ".sea", ".sen", ".sfark", ".sfx", ".shar", ".sit", \
    ".sitx", ".sqx", ".tar", ".tbz2", ".tgz", ".tlz", ".tqt", ".uc", \
    ".uc0", ".uc2", ".uca", ".ucn", ".ue2", ".uha", ".ur2", ".war", ".web", \
    ".wim", ".x", ".xar", ".xp3", ".xz", ".yz1", ".z", ".zip", ".zipx", \
    ".zoo", ".zpaq", ".zz"
]


class YunpanSpider(SpiderEngine):

    def __init__(self):
        self.mysql = sMysql(MYSQL_DB['host'], MYSQL_DB['user'], MYSQL_DB['password'], 'yunpan')

    def format_size(num, unit='B'):
        next_unit_map = dict(B="K", K="M", M="G", G="T")
        if num > 1024:
            return format_size(num/1024, next_unit_map[unit])
        if num == 0:
            return "0%s  " % unit   # padding
        if unit == 'B':
            return "%.0f%s" % (num, unit)
        return "%.1f%s" % (num, unit)

    def get_baidu_user(self, uid):
        uurl = 'http://pan.baidu.com/pcloud/user/getinfo?bdstoken=null&query_uk=%s&t=1455973901296&channel=chunlei&clienttype=0&web=1' % uid
        data = self.sGet(uurl, 'utf8')
        user_data = json.loads(data)
        print "[--Baidu User-%s-]" % uurl
        #print user_data
        #sys.exit()
        return user_data

    def get_baidu_fans(self, uid):
        user_data = self.get_baidu_user(uid)
        total = user_data['user_info']['fans_count']
        limit = 25
        if total > 0:
            if total < limit:
                self.__get_baidu_fans(uid, 0, limit)
            else:
                pages = int(math.ceil(total/limit))
                for i in range(1, pages+1):
                    self.__get_baidu_fans(uid, i, limit, pages)

    def __get_baidu_fans(self, uid, page, limit, pages):
        host = 'http://pan.baidu.com/pcloud/friend/getfanslist'
        token = '02cc9d67ded68064a35b2497fcee0470'
        token = ''
        start = (page - 1) * limit
        url = '%s?query_uk=%s&limit=%s&start=%s&bdstoken=%s&channel=chunlei&clienttype=0&web=1' % (host, uid, limit, start, token)

        print '[--Baidu-Fans--%s/%s--]' % (page, pages)
        print url
        #url = 'http://pan.baidu.com/pcloud/friend/getfanslist?query_uk=1846303616&limit=25&start=1325&bdstoken=&channel=chunlei&clienttype=0&web=1'
        data = self.sGet(url, 'utf8')
        fans_data = json.loads(data)

        if 'fans_list' not in fans_data.keys():
            return False

        flist = fans_data['fans_list']
        #print flist
        for i in range(0, len(flist)):
            user = flist[i]
            user.pop('intro')

            _has = self.mysql.fetch_one("select * from  tmp_bd_user where fans_uk=%s" % user['fans_uk'])
            _where = "fans_uk=%s" % user['fans_uk']
            if _has is not None:
                self.mysql.dbUpdate('tmp_bd_user', user, _where)
            else:
                self.mysql.dbInsert('tmp_bd_user', user)

    def get_baidu_file(self, uid):
        #self.get_baidu_file_info(1)
        #sys.exit()
        user_data = self.get_baidu_user(uid)
        total = user_data['user_info']['pubshare_count']
        limit = 50
        if total > 0:
            if total < limit:
                self.__get_baidu_file(uid, 0)
            else:
                pages = int(math.ceil(total/limit))
                for i in range(1, pages+1):
                    self.__get_baidu_file(uid, i, limit, pages)

    def __get_baidu_file(self, uid, page, limit, pages):
        host = 'http://pan.baidu.com/pcloud/feed/getsharelist'
        start = (page - 1) * limit
        uurl = '%s?t=1455973900538&category=0&auth_type=1&request_location=share_home&query_uk=%s&limit=%s&start=%s&channel=chunlei&clienttype=0&web=1&bdstoken=null' % (host, uid, limit, start)
        print '[--Baidu-File--%s/%s--]' % (page, pages)
        print uurl
        #sys.exit()
        data = self.sGet(uurl, 'utf8')
        file_data = json.loads(data)
        if 'records' not in file_data.keys():
            return False
        if len(file_data['records']) == 0:
            return False

        flist = file_data['records']
        for i in range(0, len(flist)):
            sfile = flist[i]
            print sfile
            res = {
                'uk': sfile['uk'],
                'source_uid': sfile['source_uid'],
                'source_id': sfile['source_id'],
                'shorturl': MySQLdb.escape_string(sfile['shorturl']),
                'vCnt': sfile['vCnt'],
                'dCnt': sfile['dCnt'],
                'tCnt': sfile['tCnt'],
                'feed_type': sfile['feed_type'],
                'category': sfile['category'],
                'shareid': sfile['shareid'],
                'data_id': sfile['data_id'],
                'title': sfile['title'],
                'filecount': sfile['filecount'],
                'feed_time': sfile['feed_time'],
            }
            self.mysql.dbInsert('tmp_bd_file', res)

    #获取文件大小和fs_id
    def get_baidu_file_info(self, shorturl):
        #shorturl = '1eRoe7TK'
        url = 'http://pan.baidu.com/s/%s' % shorturl
        self.set_refer('http://pan.baidu.com/')
        data = self.sGet(url, 'utf8', 'de')
        size = self.sMatch('"size":', ',"server_mtime"', data, 0)
        fs_id = self.sMatch('"fs_id":', ',"app_id"', data, 0)
        print "[--Baidu-shorturl-%s--fsid-%s--size-%s--]" % (shorturl, fs_id[0], size[0])
        up = {'file_size': size[0], 'fs_id': fs_id[0]}
        _where = "shorturl='%s'" % shorturl
        self.mysql.dbUpdate('tmp_bd_file', up, _where)

    def get_sina_while_category(self, catid):
        self.get_sina_category(catid, 1)
        self.get_sina_category(catid, 2)

    def get_sina_category(self, catid, page):
        ##catid = 13
        url = 'http://vdisk.weibo.com/share/hot?cid=%s&page=%s' % (catid, page)
        print url
        data = self.sGet(url, 'utf8', 'de')
        shorturl = self.sMatch('"copy_ref":"', '","filename"', data, 0)
        shorturl = list(set(shorturl))
        #print shorturl
        #self.get_sina_user_file(2)
        for i in range(0, len(shorturl)):
            self.get_sina_file(shorturl[i], catid)

    '''
    def get_sina_user_file(self, uid):
        uid = 1773724425
        url = 'http://vdisk.weibo.com/u/%s' % uid
        print url
        data = self.sGet(url, 'utf8', 'de')
        info = self.sMatch("data-info='", "'><\/a>", data, 0)
        for i in range(0, len(info)):
            info_data = json.loads(info[i])
            print info_data
            sys.exit()
    '''
    def get_sina_file(self, shorturl, category):

        url = 'http://vdisk.weibo.com/s/%s' % shorturl
        print url
        data = self.sGet(url, 'utf8', 'de')
        #title = self.sMatch('<h1 class="page_down_filename">', '<\/h1>', data, 0)
        info = self.sMatch('data-info=\'', "'>", data, 0)
        info_data = json.loads(info[0])
        avatar = self.sMatch('<img width="50" height="50" src="', '"><\/a>', data, 0)
        view = self.sMatch(u'浏览：', u'次', data, 1)
        down = self.sMatch(u'下载：', u'次', data, 1)
        if 'username' not in info_data.keys():
            print "^^^^^^^^^^^^^^^^"
            return False
        infile = {
            'uk': int(info_data['uid']),
            'shorturl': MySQLdb.escape_string(shorturl),
            #'file_size': info_data['bytes'],
            #'fs_id': info_data['fid'],
            'vCnt': view[0],
            'dCnt': 0,
            'category': category,
            'title': info_data['filename'],
            #'feed_time':
        }
        if len(down):
            infile['dCnt'] = down[0]
        #print info_data.keys()

        if 'bytes' in info_data.keys():
            infile['file_size'] = info_data['bytes']
        if 'fid' in info_data.keys():
            infile['fs_id'] = info_data['fid']

        #print info_data
        #sys.exit()
        #print infile
        self.__insert_sina_file(infile)
        inuser = {
            'uid': int(info_data['uid']),
            'username': info_data['username'],
            'avatar_url': avatar[0]
        }
        self.__insert_sina_user(inuser)

    def __insert_sina_file(self, infile):
        _has = self.mysql.fetch_one("select * from tmp_sina_file where shorturl='%s'" % infile['shorturl'])
        _where = "shorturl='%s'" % infile['shorturl']
        if _has is not None:
            self.mysql.dbUpdate('tmp_sina_file', infile, _where)
        else:
            self.mysql.dbInsert('tmp_sina_file', infile)

    def __insert_sina_user(self, user):
        _has = self.mysql.fetch_one("select * from  tmp_sina_user where uid=%s" % user['uid'])
        _where = "uid=%s" % user['uid']
        if _has is not None:
            self.mysql.dbUpdate('tmp_sina_user', user, _where)
        else:
            self.mysql.dbInsert('tmp_sina_user', user)
