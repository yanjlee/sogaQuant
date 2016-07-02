# -*- coding: utf-8 -*-
import sys
import time
#video
from quant.spider.TouTiao import *
from quant.spider.TouTiaoDetail import *
#weixin
#from quant.spider.WeiXin import *
#baidu
#from quant.spider.Baidu import *

#rom quant.spider.Demo import *


def get_tt_video():
    TouTiaoSpider().run_list()


def post_tt_video():
    TouTiaoSpider().run_post()


def get_yy_video():
    TouTiaoSpider().run_yy()


def get_vlook_video():
    TouTiaoSpider().run_vlook()


def post_vlook_video():
    TouTiaoSpider().post_vlook()


if __name__ == '__main__':

    start = time.time()
    function = eval(sys.argv[1])
    function()
    end = time.time()
    print end-start
