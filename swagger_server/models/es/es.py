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
            ssl_show_warn=False,  # 忽略 SSL 警告
            timeout=120
        )
        if es.ping():
            print("Connected to Elasticsearch")
        else:
            print("Could not connect to Elasticsearch")
        return es
    except ConnectionError as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return None


def get_all_category_ids_from_es(es):
    query = {
        "query": {
            "match_all": {}
        },
        "_source": ["category_id"],
        "size": 10000  # 假设category_id不会超过10000个，如果有更多需要调整大小
    }

    response = es.search(index="biz_category", body=query)
    hits = response['hits']['hits']
    category_ids = [hit['_source']['category_id'] for hit in hits]

    return category_ids


def get_category_id_from_es(es, name):
    if name is None:
        return []
    query = {
        "query": {
            "wildcard": {
                "name.keyword": name
            }
        }
    }

    response = es.search(index="biz_category_index", body=query)
    hits = response['hits']['hits']
    category_ids = [hit['_source']['category_id'] for hit in hits]

    return category_ids


def get_category_id_from_es_name(es, industry_pattern):
    query = {
        "size": 1000,
        "query": {
            "wildcard": {
                "name.keyword": industry_pattern
            }
        }
    }
    response = es.search(index="biz_category_index", body=query)
    return [{'category_id': hit['_source']['category_id'], 'name': hit['_source']['name']} for hit in
            response['hits']['hits']]
