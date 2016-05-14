# -*- coding: UTF-8 -*-
'''
def ss (self):
    rows = [ ( 1, "First" ),
             ( 2, "Second" ),
             ( 3, "Third" ),
             ( 4, "Fourth" ),
             ( 5, "Fifth" ),
             ( 6, "Sixth" ),
             ( 7, "Seventh" ) ]
    sql = "insert into baidu.TestExecuteMany (IntCol, StringCol) values (?, ?)"
    self.cursor.executemany(sql, rows)
'''

import MySQLdb
'''
__all__ = [
    'getRecord',
    'dbQuery',
    'dbInsert',
    'dbUpdate']
'''


class sMysql:

    sqlhost = 'localhost'
    sqluser = 'root'
    sqlpwd = '1234asdf'
    sqldb = ''

    def __init__(self, dbhost, dbuser, dbpwd, dbname='', dbcharset='utf8'):
        #self.dsn = dbdsn
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpwd = dbpwd
        self.dbname = dbname
        self.dbcharset = dbcharset
        #sid = 'dsn=%s;uid=%s;pwd=%s' % (self.dsn,self.dbuser,self.dbpwd)
        self.db = MySQLdb.connect(host=self.dbhost, user=self.dbuser, passwd=self.dbpwd, db=self.dbname)
        self.db.ping(True)
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.cursor.execute("SET character_set_connection=%s, character_set_results=%s, character_set_client=binary" % (self.dbcharset, self.dbcharset))
        #db.set_character_set('utf8')
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def getRecord(self, sql, record=2, rows=10):
        self.cursor.execute(sql)
        #返回一条结果
        if record == 1:
            res = self.cursor.fetchone()
        elif record == 2:
            res = self.cursor.fetchall()
        elif record == 3:
            res = self.cursor.fetchmany(rows)
        return res

    def fetch_one(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
        return res

    def dbQuery(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        return 1

    def dbInsert(self, table, param):
        field = ",".join(param.keys())
        field_v = ",".join(["'%s'" % k for k in param.values()])
        #field_v = ''
        sql = "INSERT INTO %s(%s) VALUES (%s)" % ("%s.%s" % (self.dbname, table), field, field_v)
        #print sql
        #filename='111.txt'
        #fp=open(filename,'a+')
        #fp.write(sql)
        self.cursor.execute(sql)
        self.db.commit()

        return self.getRecord("SELECT LAST_INSERT_ID()", 1)

    def dbInsert_st(self, table, param):
        field = ",".join(param.keys())
        field_v = ",".join(["'%s'" % MySQLdb.escape_string(k) for k in param.values()])
        #field_v = ''
        sql = "INSERT INTO %s(%s) VALUES (%s)" % ("%s.%s" % (self.dbname, table), field, field_v)
        #print sql
        #filename='111.txt'
        #fp=open(filename,'a+')
        #fp.write(sql)
        self.cursor.execute(sql)
        self.db.commit()

        return self.getRecord("SELECT LAST_INSERT_ID()", 1)

    #返回句柄
    def getDB(self):
        return self.cursor

    def dbUpdate(self, table, param, where):
        sqlset = ",".join(["%s='%s'" % (k, v) for k, v in param.items()])
        sql = "UPDATE %s SET %s WHERE %s " % ("%s.%s" % (self.dbname, table), sqlset, where)
        self.cursor.execute(sql)
        self.db.commit()
        return True

    def dbClose(self):
        self.cursor.close()
        return True
        #connection.close()
