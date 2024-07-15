import json

import connexion
import six
from flask import jsonify, request, make_response

from swagger_server.models import type_req
from swagger_server.models.applicant_req import ApplicantReq  # noqa: E501
from swagger_server.models.applicant_res import ApplicantRes  # noqa: E501
from swagger_server.models.area_req import AreaReq  # noqa: E501
from swagger_server.models.area_res import AreaRes  # noqa: E501
from swagger_server.models.patent_report_req import PatentReportReq  # noqa: E501
from swagger_server.models.patent_report_res import PatentReportRes  # noqa: E501
from swagger_server.models.patent_report_detail_req import PatentReportDetailReq  # noqa: E501
from swagger_server.models.patent_report_detail_res import PatentReportDetailRes  # noqa: E501
from swagger_server.models.mysql.db import create_connection, close_connection, DecimalEncoder
from swagger_server.models.trend1_req import Trend1Req  # noqa: E501
from swagger_server.models.trend1_res import Trend1Res  # noqa: E501
from swagger_server.models.trend2_req import Trend2Req  # noqa: E501
from swagger_server.models.trend2_res import Trend2Res  # noqa: E501
from swagger_server.models.type_req import TypeReq  # noqa: E501
from swagger_server.models.type_res import TypeRes  # noqa: E501
from swagger_server import util
from datetime import datetime


def patent_applicant(body):  # noqa: E501
    """申请人分析

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: ApplicantRes
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400
    body = request.get_json()
    applicant_req = ApplicantReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT applicant_name AS applicant, COUNT(*) AS num
    FROM biz_patent
    WHERE meta_class like %s
    AND application_area_code like %s
    GROUP BY applicant_name
    ORDER BY num DESC limit 10;
    """
    like_pattern1 = f"%{applicant_req.industry}%"
    if applicant_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{applicant_req.area}%"
    if applicant_req.area is None:
        like_pattern2 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'applicant': row['applicant'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_area(body):  # noqa: E501
    """地域分析

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: AreaRes
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400
    body = request.get_json()
    area_req = AreaReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT
    application_area_code AS area,
    YEAR(application_date) AS year,
    COUNT(*) AS num
FROM
    biz_patent
WHERE
    YEAR(application_date) BETWEEN 2014 AND 2024
  AND meta_class LIKE %s
GROUP BY
    application_area_code, YEAR(application_date)
ORDER BY
    application_area_code, year;
    """
    like_pattern1 = f"%{area_req.industry}%"
    if area_req.industry is None:
        like_pattern1 = f"%%"
    cursor.execute(query, (like_pattern1,))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'year': row['year'], 'area': row['area'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_trend1(body):  # noqa: E501
    """专利趋势1

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Trend1Res
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400
    body = request.get_json()
    trend1_req = Trend1Req.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT YEAR(application_date) AS year, COUNT(*) AS num
    FROM biz_patent
    WHERE YEAR(application_date) BETWEEN 2014 AND 2024
        AND meta_class like %s
        AND application_area_code like %s
    GROUP BY YEAR(application_date)
    ORDER BY year;
    """
    like_pattern1 = f"%{trend1_req.industry}%"
    if trend1_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{trend1_req.area}%"
    if trend1_req.area is None:
        like_pattern2 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'year': row['year'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_trend2(body):  # noqa: E501
    """专利趋势2

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Trend2Res
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400
    body = request.get_json()
    trend2_req = Trend2Req.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT
    application_area_code,
    YEAR(application_date) AS year,
    SUM(CASE WHEN legal_status IN ('授权', '有效') THEN 1 ELSE 0 END) AS authorization_num,
    SUM(CASE WHEN legal_status NOT IN ('授权', '有效') THEN 1 ELSE 0 END) AS apply_num,
    CASE
        WHEN SUM(CASE WHEN legal_status IN ('授权', '有效') THEN 1 ELSE 0 END) = 0
            THEN 0
        ELSE
            SUM(CASE WHEN legal_status IN ('授权', '有效') THEN 1 ELSE 0 END) /
            SUM(CASE WHEN legal_status NOT IN ('授权', '有效') THEN 1 ELSE 0 END)
        END AS proportion
FROM
    biz_patent
WHERE
    YEAR(application_date) BETWEEN 2014 AND 2024
  AND meta_class LIKE %s
  AND application_area_code LIKE %s
GROUP BY
    application_area_code, YEAR(application_date)
ORDER BY
    application_area_code, year;
    """
    like_pattern1 = f"%{trend2_req.industry}%"
    if trend2_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{trend2_req.area}%"
    if trend2_req.area is None:
        like_pattern2 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2))
    results = cursor.fetchall()
    close_connection(connection)
    if results:
        response = {
            'data': [{'year': row['year'], 'authorization_num': row['authorization_num'], 'apply_num': row['apply_num'],
                      'proportion': row['proportion']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False, cls=DecimalEncoder)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_type(body):  # noqa: E501
    """类型分析

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: TypeRes
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400

    body = request.get_json()
    type_req = TypeReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = "SELECT patent_type, COUNT(*) as num FROM biz_patent WHERE meta_class like %s GROUP BY patent_type"
    like_pattern = f"%{type_req.industry}%"
    if type_req.industry is None:
        like_pattern = f"%%"
    cursor.execute(query, (like_pattern,))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'type': row['patent_type'], 'num': row['num']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200

def patent_report_save(body):  # noqa: E501
    """报告保存

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: PatentReportRes
    """

    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400

    body = request.get_json()
    patent_report_req = PatentReportReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)

    user_id = patent_report_req.user_id
    title = patent_report_req.title
    batch_id = patent_report_req.batch_id

    # 数据准备
    data = [
        (user_id, title, datetime.now(), datetime.now(), 1, 0, batch_id)
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
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'insert fail'}), 500
def patent_report_detail_save(body):  # noqa: E501
    """报告详情保存

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: None
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400

    body = request.get_json()
    patent_report_detail_req = PatentReportDetailReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)

    report_id = patent_report_detail_req.report_id
    type = patent_report_detail_req.type
    sub_title = patent_report_detail_req.sub_title
    content = patent_report_detail_req.content
    json_data = patent_report_detail_req.data

    # 数据准备
    datas = [
        (report_id, type,sub_title,content,json_data, datetime.now(), datetime.now(), 1, 0)
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
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'insert fail'}), 500
