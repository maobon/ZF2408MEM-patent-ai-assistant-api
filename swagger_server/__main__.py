#!/usr/bin/env python3

import connexion
import mysql
from elasticsearch import helpers
from flask import jsonify

from swagger_server.job.sync_patent_to_dify import SyncPatentToDify
from swagger_server.controllers.create_pdf import createPdf

from swagger_server import encoder
from flask_cors import CORS

from swagger_server.models.es.es import create_es_connection
from swagger_server.models.mysql.db import create_connection


def main():
    app = connexion.FlaskApp(__name__, specification_dir='./swagger/')
    CORS(app.app, resources={
        r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*",
                "supports_credentials": True}})
    # scheduler = SyncPatentToDify(app)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'API Demo'}, pythonic_params=True)
    # 获取底层的 Flask 应用
    flask_app = app.app
    # 定义非 Swagger 的蓝图
    flask_app.register_blueprint(createPdf)

    app.run(host='0.0.0.0', port=22440)


def _build_cors_preflight_response():
    response = jsonify()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# 从MySQL提取数据
def fetch_data_from_mysql():
    db_connection = create_connection()

    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM biz_category WHERE category_id IS NOT NULL")
    rows = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return rows


# 将数据导入Elasticsearch
def import_data_to_es(rows):
    es = create_es_connection()
    actions = [
        {
            "_index": "biz_category_index",
            "_id": row["id"],
            "_source": {
                "name": row["name"],
                "level": row["level"],
                "pid": row["pid"],
                "pname": row["pname"],
                "source": row["source"],
                "source_name": row["source_name"],
                "type": row["type"],
                "category_id": row["category_id"],
                "create_date": row["create_date"].strftime('%Y-%m-%d %H:%M:%S') if row["create_date"] else None
            }
        }
        for row in rows
    ]

    helpers.bulk(es, actions)


if __name__ == '__main__':
    main()
