import logging
import os
import sqlite3 as sqlite
from be.model.orm_models import createTable
#from orm_models import createTable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from contextlib import contextmanager
import psycopg2


class Store:
    #database: str

    def __init__(self):
        self.database = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/bookstore.db")
        # 最后我们只要换掉这个db_address就可以换成psql
        self.engine = create_engine("sqlite:///"+self.database)
        '''
        self.engine = create_engine("postgresql+psycopg2://stu10205501460:Stu10205501460@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10205501460",
        max_overflow=0,
        # 链接池大小
        pool_size=10,
        # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
        pool_timeout=5,
        # 多久之后对链接池中的链接进行一次回收
        pool_recycle=5,
        # 查看原生语句（未格式化）
        echo=True
        )
        '''
        
        #self.engine = create_engine("postgresql+psycopg2://postgres:123456@localhost:5432/postgres",echo=True)
        self.DBSession = sessionmaker(bind=self.engine)
        self.init_tables()


    def init_tables(self):

        createTable(self.engine)


    @contextmanager
    def get_db_session(self):
        try:
            session = scoped_session(self.DBSession)
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.remove()


database_instance: Store = None


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_session()

if __name__ == "__main__":
    init_database()