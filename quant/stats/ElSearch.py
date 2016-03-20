# -*- coding: utf-8 -*-
from quant.core.Stats import *
from elasticsearch import Elasticsearch


class ElSearch(StatsEngine):

    def __init__(self, args):
        StatsEngine.__init__(self)
        self.args = args

    def run(self):
        print self.args
        es = Elasticsearch(host=ES_CONFIG['host'], port=ES_CONFIG['port'])
        today = self.tools.d_date('%Y%m%d')
        today = 20160318

        data = self.mysql.getRecord("select * from s_stock_list where dateline=%s " % today)
        tags = self.mysql.getRecord("select s_code,category_name from s_stock_cate_list where 1")
        tags_list = {}
        for row in tags:
            if row['s_code'] not in tags_list.keys():
                tags_list[row['s_code']] = [row['category_name']]
            else:
                tags_list[row['s_code']].append(row['category_name'])

        i = 1
        for row in data:
            tagss = ''
            if row['s_code'] in tags_list.keys():
                tags_ids = tags_list[row['s_code']]
                tagss = ','.join(list(set(tags_ids)))
            #取财务指标
            s_code = row['s_code']
            #s_code = 'sh600836'
            tes = self.mysql.fetch_one("select * from s_company_finance where code=%s order by reportdate desc limit 1" % s_code[2:])

            if tes is None:
                tes = {
                    'reportdate': 0,
                    'basiceps': 0,
                    'epsweighted': 0,
                    'epsdiluted': 0,
                    'naps': 0,
                    'opercashpershare': 0,
                    'peropecashpershare': 0,
                    'netassgrowrate': 0,
                    'netincgrowrate': 0,
                    'salegrossprofitrto': 0,
                }

            average = self.mysql.fetch_one("select * from s_stock_average where s_code ='%s' and dateline=%s" % (s_code, today))
            if average is None:
                average = {'on_ma5': 0, 'on_ma10': 0, 'on_ma20': 0, 'on_ma30': 0, 'on_ma60': 0}

            doc = {
                's_code': s_code,
                'name': row['name'],
                'tagss': tagss,
                'last_close': row['last_close'],
                'open': row['open'],
                'close': row['close'],
                'high': row['high'],
                'low': row['low'],
                'chg': row['chg'],
                'chg_m': row['chg_m'],
                'volumes': row['volumes']/100,
                'amount': row['amount']/10000,
                'now_zf': row['now_zf'],
                'turnover': row['turnover'],
                'run_market': row['run_market']/100000000,
                'all_market': row['all_market']/100000000,
                'reportdate': tes['reportdate'],
                'basiceps': tes['basiceps'],                 # 基本每股收益
                'epsweighted': tes['epsweighted'],              # 每股收益(加权)
                'epsdiluted': tes['epsdiluted'],               # 每股收益(摊薄)
                'naps': tes['naps'],                     # 每股净资产
                'opercashpershare': tes['opercashpershare'],         # 每股现金流
                'peropecashpershare': tes['peropecashpershare'],       # 每股经营性现金流
                'netassgrowrate': tes['netassgrowrate'],           # 净资产增长率(%)
                'netincgrowrate': tes['netincgrowrate'],          # 净利润增长率(%)
                'salegrossprofitrto': tes['salegrossprofitrto'],      # 销售毛利率

                'on_ma5': average['ma5'],
                'on_ma10': average['ma10'],
                'on_ma20': average['ma20'],
                'on_ma30': average['ma30'],
                'on_ma60': average['ma60'],
            }
            es.index(index="stock8", doc_type='info', id=i, body=doc)
            i += 1
        es.indices.refresh(index="stock8")
