# -*- coding: utf-8 -*-
#import sys
#import pymongo
from elasticsearch import Elasticsearch

'''

    #es.put_mapping("stock_list", {'properties': mapping}, ["stock_list"])

    curl -XDELETE localhost:9200/stock_list?pretty
    curl -XDELETE localhost:9200/stock_list/stock/2?pretty
    conn = ES('127.0.0.1:9200')
    for item in Data().getData():
        #添加索引
        conn.index(item,"test-index", "test-type",item['id'])

    #索引优化
    conn.optimize(["test-index"])
    #删除索引内容
    conn.delete("test-index", "test-type", 2668090)
    #更新索引内容
    model = conn.get("test-index", "test-type", 2667371)
    model["title"]="标题修改测试"
    conn.update(model,"test-index", "test-type",2667371)

    #刷新索引
    conn.refresh(["test-index"])


curl -XPOST http://localhost:9200/stock2/ -d'
{
  "mappings": {
        "stock": {
            "properties": {
                "name": {
                    "type": "string",
                    "analyzer": "ik_max_word",
                    "store": "no",
                    "term_vector": "with_positions_offsets",
                    "search_analyzer": "ik_max_word",
                    "include_in_all": "true",
                    "boost": 8
                },
                "tags": {
                    "type": "string",
                    "analyzer": "ik_max_word",
                    "store": "no",
                    "term_vector": "with_positions_offsets",
                    "search_analyzer": "ik_max_word",
                    "include_in_all": "true",
                    "boost": 8
                }
            }
        }
    }
}'



curl -XPOST http://localhost:9200/stock8/info/_mapping -d'
{
    "info": {
             "_all": {
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_max_word",
            "term_vector": "no",
            "store": "false"
        },
        "properties": {
            "name": {
                "type": "string",
                "store": "no",
                "term_vector": "with_positions_offsets",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
                "include_in_all": "true",
                "boost": 8
            },
            "tagss": {
                "type": "string",
                "store": "no",
                "term_vector": "with_positions_offsets",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
                "include_in_all": "true",
                "boost": 8
            }
        }
    }
}'

curl -XPOST http://localhost:9200/stock8/info/_search  -d'
{
    "query" : { "match" : { "tagss" : "迪斯尼" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "name" : {}
        }
    }
}'

    '''
def main_search():
    #conn = pyes.ES('127.0.0.1:9200')
    es = Elasticsearch()
    '''
    使用match_all 可以查询到所有文档，是没有查询条件下的默认语句
    {
        "match_all": {}
    }
    match查询是一个标准查询，不管你需要全文本查询还是精确查询
    multi_match 查询允许你做match查询的基础上同时搜索多个字段
    query_body = {
        "query": {
            "match": {
                "s_code": "300"
            }
        }
    }

    #######
    bool 查询与 bool 过滤相似，用于合并多个查询子句。不同的是，bool 过滤可以直接给出是否匹配成功， 而bool 查询要计算每一个查询子句的 _score
    合并多子句
    {
        "bool": {
            "must": { "match":      { "email": "business opportunity" }},
            "should": [
                 { "match":         { "starred": true }},
                 { "bool": {
                       "must":      { "folder": "inbox" }},
                       "must_not":  { "spam": true }}
                 }}
            ],
            "minimum_should_match": 1
        }
    }
    term主要用于精确匹配哪些值，比如数字，日期，布尔值或 not_analyzed的字符串(未经分析的文本数据类型)
    { "term": { "age":    26           }}
    terms 跟 term 有点类似，但 terms 允许指定多个匹配条件
    {
    "terms": {
        "tag": [ "search", "full_text", "nosql" ]
        }
    }
gt :: 大于
gte:: 大于等于
lt :: 小于
lte:: 小于等于
    {
        "range": {
            "run_market": {"gte": 40, "lt": 43}
        }
    }

exists 和 missing 过滤可以用于查找文档中是否包含指定字段或没有某个字段，类似于SQL语句中的IS_NULL条件
    {
    "exists":   {
        "field":    "title"
    }
}
search API中只能包含 query 语句，所以我们需要用 filtered 来同时包含 "query" 和 "filter" 子句
{
    "query": {
        "filtered": {
            "query":  { "match": { "email": "business opportunity" }},
            "filter": { "term": { "folder": "inbox" }}
        }
    }
}
匹配全部邮件
{
    "query": {
        "filtered": {
            "query":    { "match_all": {}},
            "filter":   { "term": { "folder": "inbox" }}
        }
    }
}

查询语句中的过滤

有时候，你需要在 filter 的上下文中使用一个 query 子句。下面的语句就是一条带有查询功能 的过滤语句， 这条语句可以过滤掉看起来像垃圾邮件的文档
{
    "query": {
        "filtered": {
            "filter":   {
                "bool": {
                    "must":     { "term":  { "folder": "inbox" }},
                    "must_not": {
                        "query": { <1>
                            "match": { "email": "urgent business proposal" }
                        }
                    }
                }
            }
        }
    }
}
query_body = {
        "query": {
            "range": {
                "run_market": {"gte": 40, "lt": 43}
            }
        }
    }


    query_body = {
        "query": {"match": {"tagss": "迪斯尼"}},
        "highlight": {
            "pre_tags": ["<tag1>", "<tag2>"],
            "post_tags": ["</tag1>", "</tag2>"],
            "fields": {
                "name": {}
            }
        }
    }
    '''

    query_body = {
        'query': {
            'bool': {
                'must': [
                    {"match": {"tagss": "迪斯尼"}},
                    {"range": {"run_market": {"gte": 40, "lt": 100}}}
                ],
                'should': [],
                'must_not': []
            },
            #"filtered": {"filter": {}}
        }
    }
    results = es.search(index="stock8", doc_type='info', body=query_body)
    print("Got %d Hits:" % results['hits']['total'])
    print results
    #查询name中包含 百度 的数据
    #q = pyes.StringQuery(u"百 度",'name')
    #for r in results:
        #print r._meta
    #print results


if __name__ == '__main__':
    #初始化策略类

    main_search()