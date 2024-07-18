from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine, MetaData, Table, asc, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
import requests
import atexit
import logging
from datetime import datetime

# 配置日志记录
logging.basicConfig(level=logging.INFO)


class SyncPatentToDify:
    """
        db:
          #  host: 10.2.16.220:3306
          #  pass: Tiger!654123#Root
          user: root
          host: 47.94.110.191:9005
          pass: Tiger!123456
          db1: ks_sd_scholar
          db2: patent_spider
        """

    def __init__(self, app=None):

        # 数据库 URL
        self.DATABASE_URL = "mysql+mysqlconnector://root:Tiger!123456@47.94.110.191:9005/ks_sd_scholar"

        # 外部接口 URL ffc48542-c907-4d2b-abee-916c7d7b90c7是数据集id
        self.EXTERNAL_API_URL = "http://110.42.103.198:23837/v1/datasets/ffc48542-c907-4d2b-abee-916c7d7b90c7/document/create_by_text"

        # HTTP 头信息
        self.HEADERS = {
            'Authorization': 'Bearer dataset-XvEmX2yTpra9QnzoF9UwfrtE',
            'Content-Type': 'application/json'
        }

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # 创建数据库连接
        self.engine = create_engine(self.DATABASE_URL)
        self.metadata = MetaData()

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # 专利表biz_patent
        # self.data_table = Table('biz_patent', self.metadata, autoload_with=self.engine)

        self.data_table = Table(
            'biz_patent', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('application_date', String(64)),
            Column('legal_status', String(255)),
            Column('applicant_name', String(255)),
            Column('application_area_code', String(255)),
            Column('meta_class', String(128)),
            Column('patent_type', String(255)),
            Column('title', String(255)),
            Column('signory', String(2048)),
            Column('summary', String(2048)),
            Column('update_time', DateTime)
        )

        # 调度任务，每1分钟运行一次
        self.scheduler.add_job(
            func=self.scheduled_task,
            trigger=IntervalTrigger(minutes=1),
            id='sync_patent_to_dify',
            name='Run sync_patent_to_dify task every 1 minutes',
            replace_existing=True)

        # 关闭调度器
        atexit.register(lambda: self.scheduler.shutdown())

    def scheduled_task(self):
        try:
            logging.info("sync_patent_to_dify task is running...")
            # 执行任务
            page = 0
            page_size = 100  # 每页大小
            while True:
                results = self.query_database(page, page_size)
                if not results:
                    break
                for result in results:
                    data_dict = {
                        "id": result.id,
                        "application_date": result.application_date,
                        "legal_status": result.legal_status,
                        "applicant_name": result.applicant_name,
                        "application_area_code": result.application_area_code,
                        "meta_class": result.meta_class,
                        "patent_type": result.patent_type,
                        "title": result.title,
                        "signory": result.signory,
                        "summary": result.summary,
                        "update_time": result.update_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    requestBody = {
                        "indexing_technique": "high_quality",
                        "process_rule": {"mode": "automatic"},
                        "name": result.id,
                        "text": data_dict
                    }
                    status_code, response_text = self.call_external_api(requestBody)
                    logging.info(f"Status Code: {status_code}, Response: {response_text}")
                page += 1
        except Exception as e:
            logging.error(f"Error occurred: {e}")

    def query_database(self, page, page_size):
        # 分页查询数据库中的数据，并按更新时间升序排序
        offset = page * page_size
        query = select(self.data_table).order_by(asc(self.data_table.c.update_time)).limit(page_size).offset(offset)
        result = self.session.execute(query).fetchall()
        return result

    def call_external_api(self, data):
        # 调用外部接口并传入头信息
        response = requests.post(self.EXTERNAL_API_URL, json=data, headers=self.HEADERS)
        return response.status_code, response.text
