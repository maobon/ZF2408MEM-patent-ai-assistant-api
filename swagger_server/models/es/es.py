from flask import Flask, request, jsonify, make_response
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, RequestError


def create_es_connection():
    """Create a connection to the Elasticsearch cluster."""
    try:
        es = Elasticsearch(
            ['http://47.94.110.191:9006'],
            http_auth=('admin', 'Standard!123654'),
            verify_certs=False,  # 忽略证书验证
            ssl_show_warn=False  # 忽略 SSL 警告
        )
        if es.ping():
            print("Connected to Elasticsearch")
        else:
            print("Could not connect to Elasticsearch")
        return es
    except ConnectionError as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return None
