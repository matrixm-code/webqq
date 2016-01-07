# -*- coding:utf-8 -*-

'''
    数据库连接
'''
import MySQLdb

# class ClassDb(object):
#     def connect(self,**args):
#         ##连接数据库
#         self.host = args['host']
#         self.port = args['port']
#         self.user = args['user']
#         self.passwd = args['passwd']
#         self.db = args['db']
#         self.charset = args['charset']
#         try:
#             self.conn = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db,charset=self.charset)
#             self.cursor = self.conn.cursor()
#         except Exception, err:
#             print str(err)
#
#     def execute(self,sql):
#         #执行语句
#         try:
#             self.cursor.execute(sql)
#         finally:
#             pass
#         self.conn.commit()
#
#     def fetchall(self):
#         return self.cursor.fetchall()       #元组类型
#
#     def fetchone(self):
#         return self.cursor.fetchone()       #字典类型

if __name__ == '__main__':
    # db = ClassDb()
    # db.connect(host='118.26.204.253',user='root',port=3306,db='luoshen_360_S1001',passwd='LongHun@Game',charset='utf-8')
    # db.execute('show tables')
    # db.fetchall()
    connect = MySQLdb.connect(host='118.26.204.253',user='root',port=3306,passwd='LongHun@Game')
    cursor = connect.cursor()
    cursor.execute('create database lzx')
    print cursor.fetchall()



