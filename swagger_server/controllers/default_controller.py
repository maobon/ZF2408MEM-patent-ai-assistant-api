import json
from datetime import datetime

import connexion
import six
from elasticsearch import exceptions
from flask import jsonify, request, make_response
from mysql.connector import Error

from swagger_server.models import type_req, DetailReq, ListReq, DeleteReq
from swagger_server.models.applicant_req import ApplicantReq  # noqa: E501
from swagger_server.models.applicant_res import ApplicantRes  # noqa: E501
from swagger_server.models.area_req import AreaReq  # noqa: E501
from swagger_server.models.area_res import AreaRes  # noqa: E501
from swagger_server.models.cors.cors import make_cors_response
from swagger_server.models.es.es import create_es_connection, get_category_id_from_es
from swagger_server.models.patent_report_req import PatentReportReq  # noqa: E501
from swagger_server.models.patent_report_res import PatentReportRes  # noqa: E501
from swagger_server.models.patent_report_detail_req import PatentReportDetailReq  # noqa: E501
from swagger_server.models.patent_report_detail_res import PatentReportDetailRes  # noqa: E501
from swagger_server.models.mysql.db import create_connection, close_connection, DecimalEncoder
from swagger_server.models.concentration_req import ConcentrationReq  # noqa: E501
from swagger_server.models.concentration_res import ConcentrationRes  # noqa: E501
from swagger_server.models.mysql.db import close_connection, create_connection, DecimalEncoder, create_connection1
from swagger_server.models.technology_req import TechnologyReq  # noqa: E501
from swagger_server.models.technology_res import TechnologyRes  # noqa: E501
from swagger_server.models.trend1_req import Trend1Req  # noqa: E501
from swagger_server.models.trend1_res import Trend1Res  # noqa: E501
from swagger_server.models.trend2_req import Trend2Req  # noqa: E501
from swagger_server.models.trend2_res import Trend2Res  # noqa: E501
from swagger_server.models.type_req import TypeReq  # noqa: E501
from swagger_server.models.type_res import TypeRes  # noqa: E501
from swagger_server import util
from swagger_server import date_util


def patent_applicant_options():  # noqa: E501
    """CORS support for 申请人分析

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_applicant(body):  # noqa: E501
    """申请人分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: ApplicantRes
    """
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)
    body = request.get_json()
    applicant_req = ApplicantReq.from_dict(body)

    es = create_es_connection()
    if es is None:
        return make_cors_response(jsonify({'message': 'Elasticsearch connection failed'}), 500)

    # 获取分类ID
    name_pattern = f"*{applicant_req.industry}*" if applicant_req.industry else "*"
    category_ids = get_category_id_from_es(es, name_pattern) if applicant_req.industry else []

    area_pattern = f"*{applicant_req.area}*" if applicant_req.area else "*"
    key_pattern = f"*{applicant_req.key}*" if applicant_req.key else "*"
    theme_pattern = f"*{applicant_req.theme}*" if applicant_req.theme else "*"

    must_clauses = []
    should_clauses = []

    if category_ids:
        should_clauses = [{"wildcard": {"class_code": f"*{category_id}*"}} for category_id in category_ids]

    if applicant_req.area:
        must_clauses.append({"wildcard": {"application_area_code": area_pattern}})
    if applicant_req.key:
        must_clauses.append({"wildcard": {"summary.keyword": key_pattern}})
    if applicant_req.theme:
        must_clauses.append({"wildcard": {"title.keyword": theme_pattern}})

    if not must_clauses and not should_clauses:
        query = {
            "size": 0,
            "query": {
                "match_all": {}
            },
            "aggs": {
                "top_applicants": {
                    "terms": {
                        "field": "applicant_name.keyword",
                        "size": 5,
                        "order": {"_count": "desc"}
                    }
                }
            }
        }
    else:
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": should_clauses,
                    "minimum_should_match": 1 if should_clauses else 0
                }
            },
            "aggs": {
                "top_applicants": {
                    "terms": {
                        "field": "applicant_name.keyword",
                        "size": 5,
                        "order": {"_count": "desc"}
                    }
                }
            }
        }

    print(query)

    try:
        response = es.search(index="patent2", body=query)
        results = response['aggregations']['top_applicants']['buckets']

        data = [{'applicant': result['key'], 'num': result['doc_count']} for result in results]

        response_json = json.dumps({'data': data}, ensure_ascii=False)
        return make_cors_response(response_json, 200)

    except Exception as e:
        print(f"Error executing query: {e}")
        return make_cors_response(jsonify({'message': 'Error executing query'}), 500)


def patent_area_options():  # noqa: E501
    """CORS support for 地域分析

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_area(body):  # noqa: E501
    """地域分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: AreaRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)
    body = request.get_json()
    area_req = AreaReq.from_dict(body)

    es = create_es_connection()
    if es is None:
        return make_cors_response(jsonify({'message': 'Elasticsearch connection failed'}), 500)

    meta_class_pattern = f"*{area_req.industry}*" if area_req.industry else "*"
    category_ids = get_category_id_from_es(es, meta_class_pattern) if area_req.industry else []

    summary_pattern = f"*{area_req.key}*" if area_req.key else "*"
    title_pattern = f"*{area_req.theme}*" if area_req.theme else "*"

    must_clauses = []
    should_clauses = []

    if category_ids:
        should_clauses = [{"wildcard": {"class_code": f"*{category_id}*"}} for category_id in category_ids]

    if area_req.key:
        must_clauses.append({"match": {"summary.keyword": summary_pattern}})
    if area_req.theme:
        must_clauses.append({"match": {"title.keyword": title_pattern}})

    if not must_clauses and not should_clauses:
        query = {
            "size": 0,
            "query": {
                "match_all": {}
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
    else:
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": should_clauses,
                    "minimum_should_match": 1 if should_clauses else 0
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
    print(query)
    try:
        response = es.search(index="patent2", body=query)
        top_areas = response['aggregations']['top_areas']['buckets']
        top_areas_list = [area['key'] for area in top_areas]

        if len(top_areas_list) < 5:
            top_areas_list.extend([''] * (5 - len(top_areas_list)))  # 确保有5个元素

        # 获取这些地域的每年数据
        yearly_filter = [{"terms": {"application_area_code": top_areas_list}},
                         {"range": {"application_date": {"gte": "2014", "lte": "2024"}}}]
        if category_ids:
            yearly_filter.append({"bool": {"should": [{"wildcard": {"class_code": f"*{category_id}*"}} for category_id in category_ids]}})
        if area_req.key:
            yearly_filter.append({"match": {"summary": summary_pattern}})
        if area_req.theme:
            yearly_filter.append({"match": {"title": title_pattern}})

        # 获取这些地域的每年数据
        yearly_query = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": yearly_filter
                }
            },
            "aggs": {
                "areas": {
                    "terms": {
                        "field": "application_area_code",
                        "size": 5
                    },
                    "aggs": {
                        "years": {
                            "terms": {
                                "script": {
                                    "source": "doc['application_date'].value.substring(0, 4)",
                                    "lang": "painless"
                                },
                                "size": 10,
                                "order": {
                                    "_key": "asc"
                                }
                            }
                        }
                    }
                }
            }
        }

        print(yearly_query)

        response = es.search(index="patent2", body=yearly_query)
        areas = response['aggregations']['areas']['buckets']

        # 初始化年份和区域数据结构
        years = [2017, 2018, 2019, 2020, 2021]
        areas_dict = {year: {} for year in years}

        for area in areas:
            area_key = area['key']
            for year in area['years']['buckets']:
                year_key = int(year['key'])
                if year_key in areas_dict:
                    areas_dict[year_key][area_key] = year['doc_count']

        # 构建返回结构
        response_data = {
            'year': years,
            'areas': []
        }

        # 通过所有可能的区域来填充数据
        all_areas = set(area for year_data in areas_dict.values() for area in year_data.keys())

        for area in all_areas:
            area_data = {
                'area': area,
                'data': [areas_dict[year].get(area, 0) for year in years]
            }
            response_data['areas'].append(area_data)

        return make_cors_response(jsonify(response_data), 200)

    except Exception as e:
        print(f"Error executing query: {e}")
        return make_cors_response(jsonify({'message': 'Error executing query'}), 500)

def patent_trend1_options():  # noqa: E501
    """CORS support for 专利趋势1

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_trend1(body):  # noqa: E501
    """专利趋势1

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Trend1Res
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)
    body = request.get_json()
    trend1_req = Trend1Req.from_dict(body)

    es = create_es_connection()
    if es is None:
        return make_cors_response(jsonify({'message': 'Elasticsearch connection failed'}), 500)

    industry_pattern = f"*{trend1_req.industry}*" if trend1_req.industry else "*"
    category_ids = get_category_id_from_es(es, industry_pattern)

    if not category_ids:
        return make_cors_response(jsonify({'message': 'No matching category IDs found'}), 200)

    summary_pattern = f"*{trend1_req.key}*" if trend1_req.key else "*"
    title_pattern = f"*{trend1_req.theme}*" if trend1_req.theme else "*"
    area_pattern = f"*{trend1_req.area}*" if trend1_req.area else "*"

    current_year = datetime.now().year
    start_year = current_year - 10

    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"bool": {"should": [{"wildcard": {"class_code": f"*{id}*"}} for id in category_ids]}},
                    {"wildcard": {"summary.keyword": summary_pattern}},
                    {"wildcard": {"title.keyword": title_pattern}},
                    {"wildcard": {"application_area_code": area_pattern}},
                    {"range": {"application_date": {"gte": f"{start_year}-01-01", "lte": f"{current_year}-12-31"}}}
                ]
            }
        },
        "aggs": {
            "years": {
                "terms": {
                    "field": "application_date",
                    "script": {
                        "source": "doc['application_date'].value.substring(0, 4)",
                        "lang": "painless"
                    },
                    "size": 10,
                    "order": {
                        "_key": "asc"
                    }
                }
            }
        }
    }

    try:
        response = es.search(index="patent2", body=query)
        results = response['aggregations']['years']['buckets']

        response_data = {
            'data': [{'year': int(year['key']), 'num': year['doc_count']} for year in results]
        }

        return make_cors_response(jsonify(response_data), 200)

    except (exceptions.ConnectionError, exceptions.RequestError) as e:
        print(f"Error executing query: {e}")
        return make_cors_response(jsonify({'message': 'Error executing query'}), 500)


def patent_trend2_options():  # noqa: E501
    """CORS support for 专利趋势2

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_trend2(body):  # noqa: E501
    """专利趋势2

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Trend2Res
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)
    body = request.get_json()
    trend2_req = Trend2Req.from_dict(body)

    es = create_es_connection()
    if es is None:
        return make_cors_response(jsonify({'message': 'Elasticsearch connection failed'}), 500)

    industry_pattern = f"*{trend2_req.industry}*" if trend2_req.industry else "*"
    category_ids = get_category_id_from_es(es, industry_pattern)

    if not category_ids:
        return make_cors_response(jsonify({'message': 'No matching category IDs found'}), 200)

    summary_pattern = f"*{trend2_req.key}*" if trend2_req.key else "*"
    title_pattern = f"*{trend2_req.theme}*" if trend2_req.theme else "*"
    area_pattern = f"*{trend2_req.area}*" if trend2_req.area else "*"

    current_year = datetime.now().year
    start_year = current_year - 10

    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"bool": {"should": [{"wildcard": {"class_code": f"*{id}*"}} for id in category_ids]}},
                    {"wildcard": {"summary.keyword": summary_pattern}},
                    {"wildcard": {"title.keyword": title_pattern}},
                    {"wildcard": {"application_area_code": area_pattern}},
                    {"range": {"application_date": {"gte": f"{start_year}-01-01", "lte": f"{current_year}-12-31"}}}
                ]
            }
        },
        "aggs": {
            "years": {
                "terms": {
                    "script": {
                        "source": "doc['application_date'].value.substring(0, 4)",
                        "lang": "painless"
                    },
                    "size": 10,
                    "order": {
                        "_key": "asc"
                    }
                },
                "aggs": {
                    "top5": {
                        "bucket_sort": {
                            "sort": [
                                {"_key": {"order": "asc"}}
                            ],
                            "size": 5
                        }
                    },
                    "authorization_num": {
                        "sum": {
                            "script": {
                                "source": "doc['legal_status'].value == '授权' || doc['legal_status'].value == '有效' ? 1 : 0",
                                "lang": "painless"
                            }
                        }
                    },
                    "apply_num": {
                        "sum": {
                            "script": {
                                "source": "doc['legal_status'].value != '授权' && doc['legal_status'].value != '有效' ? 1 : 0",
                                "lang": "painless"
                            }
                        }
                    }
                }
            }
        }
    }

    try:
        response = es.search(index="patent2", body=query)
        results = response['aggregations']['years']['buckets']

        response_data = {
            'data': [{'year': int(year['key']),
                      'authorization_num': year['authorization_num']['value'],
                      'apply_num': year['apply_num']['value'],
                      'proportion': (year['authorization_num']['value'] / year['apply_num']['value']) if
                      year['apply_num']['value'] > 0 else 0}
                     for year in results]
        }

        return make_cors_response(jsonify(response_data), 200)

    except (exceptions.ConnectionError, exceptions.RequestError) as e:
        print(f"Error executing query: {e}")
        return make_cors_response(jsonify({'message': 'Error executing query'}), 500)


def patent_type_options():  # noqa: E501
    """CORS support for 类型分析

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_type(body):  # noqa: E501
    """类型分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: TypeRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    type_req = TypeReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)
    query = """SELECT patent_type, COUNT(*) as num FROM biz_patent_0713 WHERE meta_class like %s and summary like %s and
             title like %s GROUP BY patent_type LIMIT 5;"""
    like_pattern = f"%{type_req.industry}%"
    if type_req.industry is None:
        like_pattern = f"%%"
    like_pattern2 = f"%{type_req.key}%"
    if type_req.key is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{type_req.theme}%"
    if type_req.theme is None:
        like_pattern3 = f"%%"
    cursor.execute(query, (like_pattern, like_pattern2, like_pattern3))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'type': row['patent_type'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'No data found'}), 200)


def patent_report_save_options():  # noqa: E501
    """CORS support for 报告保存

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_report_save(body):  # noqa: E501
    """报告保存

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: PatentReportRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    patent_report_req = PatentReportReq.from_dict(body)

    connection = create_connection1()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)

    user_id = patent_report_req.user_id
    title = patent_report_req.title
    batch_id = patent_report_req.batch_id

    # 数据准备
    data = [
        (user_id, title, date_util.getNowDateTime(), date_util.getNowDateTime(), 1, 0, batch_id)
    ]

    # SQL语句
    sql_insert = """
    INSERT INTO patent_ai_assistant.biz_patent_report 
    (user_id, title, created_time, modified_time, status, is_deleted, batch_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # 执行插入
    cursor.executemany(sql_insert, data)

    # 获取自增ID
    inserted_id = cursor.lastrowid

    # 提交事务
    connection.commit()

    # 关闭游标和连接
    cursor.close()
    close_connection(connection)

    if inserted_id:
        response = {
            'data': {'id': inserted_id}
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'insert fail'}), 500)


def patent_report_detail_save_options():  # noqa: E501
    """CORS support for 报告详情保存

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_report_detail_save(body):  # noqa: E501
    """报告详情保存

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: None
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    patent_report_detail_req = PatentReportDetailReq.from_dict(body)

    connection = create_connection1()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)

    report_id = patent_report_detail_req.report_id
    type = patent_report_detail_req.type
    sub_title = patent_report_detail_req.sub_title
    content = patent_report_detail_req.content
    json_data = patent_report_detail_req.data

    # 数据准备
    datas = [
        (report_id, type, sub_title, content, json_data, date_util.getNowDateTime(), date_util.getNowDateTime(), 1, 0)
    ]

    # SQL语句
    sql_insert = """
    INSERT INTO patent_ai_assistant.biz_patent_report_detail 
    (report_id, type,sub_title,content,data, created_time, modified_time, status, is_deleted) 
    VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)
    """

    # 执行插入
    cursor.executemany(sql_insert, datas)

    # 获取自增ID
    inserted_id = cursor.lastrowid

    # 提交事务
    connection.commit()

    # 关闭游标和连接
    cursor.close()
    close_connection(connection)

    if inserted_id:
        response = {
            'data': {'id': inserted_id}
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'insert fail'}), 500)


def patent_concentration_options():  # noqa: E501
    """CORS support for 集中度分析

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_concentration(body):  # noqa: E501
    """集中度分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: ConcentrationRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    concentration_req = ConcentrationReq.from_dict(body)

    es = create_es_connection()
    if es is None:
        return make_cors_response(jsonify({'message': 'Elasticsearch connection failed'}), 500)

    industry_pattern = f"*{concentration_req.industry}*" if concentration_req.industry else "*"
    category_ids = get_category_id_from_es(es, industry_pattern)

    if not category_ids:
        return make_cors_response(jsonify({'message': 'No matching category IDs found'}), 200)

    summary_pattern = f"*{concentration_req.key}*" if concentration_req.key else "*"
    title_pattern = f"*{concentration_req.theme}*" if concentration_req.theme else "*"
    area_pattern = f"*{concentration_req.area}*" if concentration_req.area else "*"

    current_year = datetime.now().year
    start_year = current_year - 10

    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"bool": {"should": [{"wildcard": {"class_code": f"*{id}*"}} for id in category_ids]}},
                    {"wildcard": {"summary.keyword": summary_pattern}},
                    {"wildcard": {"title.keyword": title_pattern}},
                    {"wildcard": {"application_area_code": area_pattern}},
                    {"range": {"application_date": {"gte": f"{start_year}-01-01", "lte": f"{current_year}-12-31"}}}
                ]
            }
        },
        "aggs": {
            "years": {
                "terms": {
                    "script": {
                        "source": "doc['application_date'].value.substring(0, 4)",
                        "lang": "painless"
                    },
                    "size": 5,
                    "order": {
                        "_key": "desc"
                    }
                },
                "aggs": {
                    "top_applicants": {
                        "terms": {
                            "field": "applicant_name.keyword",
                            "size": 10,
                            "order": {
                                "_count": "desc"
                            }
                        },
                        "aggs": {
                            "total_applications": {
                                "value_count": {
                                    "field": "applicant_name.keyword"
                                }
                            }
                        }
                    },
                    "total_applications_per_year": {
                        "value_count": {
                            "field": "applicant_name.keyword"
                        }
                    }
                }
            }
        }
    }

    try:
        response = es.search(index="patent2", body=query)
        results = response['aggregations']['years']['buckets']

        response_data = {
            'data': []
        }

        for year in results:
            top10_total = sum(applicant['doc_count'] for applicant in year['top_applicants']['buckets'])
            total_applications = year['total_applications_per_year']['value']
            proportion = (top10_total / total_applications) * 100 if total_applications > 0 else 0
            response_data['data'].append({'year': int(year['key']), 'proportion': proportion})

        return make_cors_response(jsonify(response_data), 200)

    except (exceptions.ConnectionError, exceptions.RequestError) as e:
        print(f"Error executing query: {e}")
        return make_cors_response(jsonify({'message': 'Error executing query'}), 500)


def patent_technology_options():  # noqa: E501
    """CORS support for 技术构成分析

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def patent_technology(body):  # noqa: E501
    """技术构成分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: TechnologyRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    technology_req = TechnologyReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)
    query = """  
SELECT
    meta_class as class,
    total_applications as num
FROM (
         SELECT
             meta_class,
             COUNT(*) AS total_applications
         FROM
             biz_patent_0713
         WHERE
             application_date >= DATE_SUB(CURDATE(), INTERVAL 10 YEAR)
           AND meta_class LIKE %s
           AND application_area_code LIKE %s
           AND summary like %s
           AND title like %s
         GROUP BY
             meta_class
     ) AS RecentYears
ORDER BY
    total_applications DESC
LIMIT 5;
    """
    like_pattern1 = f"%{technology_req.industry}%"
    if technology_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{technology_req.area}%"
    if technology_req.area is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{technology_req.key}%"
    if technology_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{technology_req.theme}%"
    if technology_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2, like_pattern3, like_pattern4))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'class': row['class'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'No data found'}), 200)


def report_detail_options():  # noqa: E501
    """CORS support for 报告详情

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def report_detail(body):  # noqa: E501
    """报告详情

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: DetailRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    detail_req = DetailReq.from_dict(body)
    if not detail_req.id:
        return make_cors_response(jsonify({'message': 'user id is none'}), 400)

    connection = create_connection1()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)
    query = """select * from patent_ai_assistant.biz_patent_report_detail where report_id = %s;"""

    cursor.execute(query, (detail_req.id,))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'type': row['type'], 'sub_title': row['sub_title'], 'content': row['content'],
                      "is_deleted": row['is_deleted'],
                      'status': row['status'], 'data': row['data']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'No data found'}), 200)


def report_list_options():  # noqa: E501
    """CORS support for 报告列表

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def report_list(body):  # noqa: E501
    """报告列表

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: ListRes
    """
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    list_req = ListReq.from_dict(body)
    if not list_req.user_id:
        return make_cors_response(jsonify({'message': 'user id is none'}), 400)

    connection = create_connection1()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    cursor = connection.cursor(dictionary=True)
    query = """select * from biz_patent_report where user_id = %s ORDER BY modified_time DESC;"""

    cursor.execute(query, (list_req.user_id,))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'id': row['id'], 'title': row['title'], 'status': row['status'], "is_deleted": row['is_deleted'],
                      'batch_id': row['batch_id'], 'update_time': row['modified_time'].strftime('%Y-%m-%d %H:%M:%S')}
                     for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)
    else:
        return make_cors_response(jsonify({'message': 'No data found'}), 200)


def report_delete_options():  # noqa: E501
    """CORS support for 删除报告

     # noqa: E501


    :rtype: None
    """
    return make_cors_response('', 200)


def report_delete(body):  # noqa: E501
    """删除报告

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: None
    """
    if not request.is_json:
        return make_cors_response(jsonify({'message': 'Invalid input'}), 400)

    body = request.get_json()
    ids = body.get('ids', [])
    if not ids:
        return make_cors_response(jsonify({'message': 'user id is none'}), 400)

    connection = create_connection1()
    if connection is None:
        return make_cors_response(jsonify({'message': 'Database connection failed'}), 500)

    try:
        cursor = connection.cursor()

        delete_query = "DELETE FROM biz_patent_report WHERE id IN (%s)" % ','.join(['%s'] * len(ids))
        cursor.execute(delete_query, ids)
        delete_query1 = "DELETE FROM biz_patent_report_detail WHERE report_id IN (%s)" % ','.join(['%s'] * len(ids))
        cursor.execute(delete_query1, ids)
        connection.commit()

        close_connection(connection)

        response = {'message': 'Items deleted successfully'}
        response_json = json.dumps(response, ensure_ascii=False)
        return make_cors_response(response_json, 200)

    except Error as e:
        print(f"Error: {e}")
        close_connection(connection)
        return make_cors_response(jsonify({'message': 'Failed to delete items'}), 500)
