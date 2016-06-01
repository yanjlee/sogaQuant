#! -*- coding:utf-8 -*-
from quant.core.Abstract import *


class StatsEngine(Abstract):
    '''
    统计类基类
    '''
    def test(self):
        pass

    def is_opening(self):
        #判断当前时间是否为开盘时间
        res = True
        block_time = int(self.tools.d_date('%H%M%S'))
        if (block_time > 113000 and block_time < 130000) or block_time > 153000 or block_time < 93000:
            res = False
        return res
