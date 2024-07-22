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


def get_top_areas(es, category_ids, summary_pattern, title_pattern):
    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"bool": {"should": [{"wildcard": {"class_code": f"*{id}*"}} for id in category_ids]}},
                    {"wildcard": {"summary.keyword": summary_pattern}},
                    {"wildcard": {"title.keyword": title_pattern}}
                ]
            }
        },
        "aggs": {
            "top_areas": {
                "terms": {
                    "field": "application_area_code",
                    "size": 5,
                    "order": {"_count": "desc"}
                }
            }
        }
    }
    try:
        response = es.search(index="your_index_name", body=query)
        top_areas = response['aggregations']['top_areas']['buckets']
        return [area['key'] for area in top_areas]
    except Exception as e:
        print(f"Error fetching top areas: {e}")
        return []
