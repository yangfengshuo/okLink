import datetime
import threading
import time
import pymysql as pysql
import yaml
from logger import Logger

class DataBase:
    # 实例化日志以及锁，并初始化运行需要用到的变量
    def __init__(self):
        self.sql_create_table = None
        self.logger = Logger()
        self.database_lock = threading.Lock()
        self.sql_insert = None
        self.sql_create_database = None
        self.database = None
        self.config = None
        self.read_config()
        self.__connDB()
        self.sql_sentences()
        self.execute_db()

    # 根据config中的数据连接数据库
    def __connDB(self):
        self.conn = pysql.connect(
            host=self.config.get('host'),
            port=self.config.get('port'),
            user=self.config.get('user'),
            password=self.config.get('password')
        )
        self.curr = self.conn.cursor()

    # 创建sql命令
    def sql_sentences(self, database: str = "okLink"):
        t = datetime.datetime.fromtimestamp(time.time())
        table_name = 'bitCoin'
        self.database = database
        self.sql_create_database = f"""
            create database if not exists {database};
            """
        self.sql_create_table = f"""
            create table if not exists {table_name} (
                hash char(64) primary key comment '交易哈希',
                block int comment '区块',
                t int comment '时间戳',
                input int comment 'input',
                output int comment 'output',
                input_amount char(30) comment '交易数额',
                Txn_fee char(60) comment 'gas费',
                transaction_time char(30) comment '交易时间'
            );
        """
        self.sql_insert = f"""
         INSERT IGNORE  into {database}.{table_name} (hash, block, t, input, output, input_amount, Txn_fee, transaction_time) 
                value ('%s', %d, %d, %d, %d, '%s', '%s', '%s');
        """

    # 执行SQL命令
    def execute_db(self):
        self.curr.execute(self.sql_create_database)
        self.curr.execute("use %s" % self.database)
        self.curr.execute(self.sql_create_table)
        self.conn.commit()

    # 读取config中的数据库配置文件
    def read_config(self):
        with open('config/config.yaml', 'r') as fp:
            self.config = yaml.safe_load(fp.read())
        keys = ['refresh', 'port', 'host', 'user', 'password']
        for key in keys:
            if self.config.get(key) is None:
                raise Exception("missing config key：", key)

    # 写入数据库操作，需要从OKlink中获取data数据
    def write_db(self, data:list[list]):
        try:
            with self.database_lock:
                for item in data:
                    self.curr.execute(self.sql_insert % tuple(item))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            self.logger.writer_logger(location="db.write",
                                      err=e)
            return False
