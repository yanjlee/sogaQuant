# -*- coding:utf-8 -*-
'''
'''
import sys
import unittest
import pymongo


class Test(unittest.TestCase):

    def setUp(self):
        #初始化工作
        pass

    def tearDown(self):
        #退出清理工作
        pass

    def testdata(self):
        print 12
        #sys.exit()
        '''
        client = pymongo.MongoClient('127.0.0.1', 27017)
        db = client.spider
        coll = db.s_stock_fuquan
        rows = coll.find()

        for row in rows:
            print row['code']
        '''

if __name__ == "__main__":
    unittest.main()
