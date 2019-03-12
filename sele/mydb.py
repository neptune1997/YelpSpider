#-*- coding:utf-8 -*-
import sqlite3
class database():
    def __init__(self,dbname = 'mydb'):
        self.dbname = dbname+'.db'
        self.conn = None
        self.cur = None
    def _createdb(self):
        """
        创建数据库restaurant表
        """
        dbname = self.dbname
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("drop table restaurant")###先删除同名表
            self.conn.commit()
        except:
            pass
        self.cur.execute('''create table restaurant
                        ( name TEXT NOT NULL,
                          city TEXT NOT null,
                          location TEXT ,
                          price INTEGER, 
                          rate real ,
                          reviews INTEGER,
                          pic TEXT,
                          primary key(city,name,location)
                        )''')
        self.conn.commit()
        self.cur.close()
        self.conn.close()
    def connect(self):
        """
        连接到数据库
        """
        if not self.isconnected:
            self.conn = sqlite3.connect(self.dbname)
            self.cur = self.conn.cursor()
            
    def disconnect(self):
        """
        和数据库断开连接
        """
        if self.isconnected:
            self.conn.commit()
            self.conn.close()
        
    def insert(self, datalist):
        """
        向数据库中插入数据
        Args:
            datalist: 列表类型，即将插入的数据构成的列表
        """
        assert len(datalist)==7
        if self.isconnected:
            self.cur = self.conn.cursor()
        else:
            self.connect()
        try:
            self.cur.execute('''insert into restaurant
                        values(?,?,?,?,?,?,?)''',datalist)
        except sqlite3.IntegrityError as e:
            print(datalist)
            print(e)
        self.conn.commit()

    @property
    def isconnected(self):
        """
        判断database类有没有连解到数据库
        """
        if isinstance(self.conn, sqlite3.Connection):
            try:
                self.conn.execute('''
                        select 1 from restaurant LIMIT 1;
                                ''')
                return True
            except sqlite3.ProgrammingError as e:
                return False
        else:
            return False

    @property
    def count(self):
        """
        判断数据库条目数量
        """
        if not self.isconnected:
            self.connect()
        self.cur.execute('''
        select count(1) 
        from restaurant
        ''')
        count = self.cur.fetchone()[0]
        return count
