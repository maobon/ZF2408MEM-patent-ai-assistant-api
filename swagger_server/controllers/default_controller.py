import json

import connexion
import six
from flask import jsonify, request, make_response

from swagger_server.models import type_req
from swagger_server.models.applicant_req import ApplicantReq  # noqa: E501
from swagger_server.models.applicant_res import ApplicantRes  # noqa: E501
from swagger_server.models.area_req import AreaReq  # noqa: E501
from swagger_server.models.area_res import AreaRes  # noqa: E501
from swagger_server.models.concentration_req import ConcentrationReq  # noqa: E501
from swagger_server.models.concentration_res import ConcentrationRes  # noqa: E501
from swagger_server.models.mysql.db import close_connection, create_connection, DecimalEncoder
from swagger_server.models.technology_req import TechnologyReq  # noqa: E501
from swagger_server.models.technology_res import TechnologyRes  # noqa: E501
from swagger_server.models.trend1_req import Trend1Req  # noqa: E501
from swagger_server.models.trend1_res import Trend1Res  # noqa: E501
from swagger_server.models.trend2_req import Trend2Req  # noqa: E501
from swagger_server.models.trend2_res import Trend2Res  # noqa: E501
from swagger_server.models.type_req import TypeReq  # noqa: E501
from swagger_server.models.type_res import TypeRes  # noqa: E501
from swagger_server import util


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
    FROM biz_patent_0713
    WHERE meta_class like %s
    AND application_area_code like %s
    AND summary like %s
    AND title like %s
    GROUP BY applicant_name
    ORDER BY num DESC limit 5;
    """
    like_pattern1 = f"%{applicant_req.industry}%"
    if applicant_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{applicant_req.area}%"
    if applicant_req.area is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{applicant_req.key}%"
    if applicant_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{applicant_req.theme}%"
    if applicant_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2, like_pattern3,like_pattern4))
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
    biz_patent_0713
WHERE
    YEAR(application_date) BETWEEN 2014 AND 2024
  AND meta_class LIKE %s
  AND summary like %s
    AND title like %s
GROUP BY
    application_area_code, YEAR(application_date)
ORDER BY
    application_area_code, year;
    """
    like_pattern1 = f"%{area_req.industry}%"
    if area_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern3 = f"%{area_req.key}%"
    if area_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{area_req.theme}%"
    if area_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1,like_pattern3, like_pattern4))
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
    FROM biz_patent_0713
    WHERE YEAR(application_date) BETWEEN 2014 AND 2024
        AND meta_class like %s
        AND application_area_code like %s
        AND summary like %s
        AND title like %s
    GROUP BY YEAR(application_date)
    ORDER BY year
    LIMIT 5;
    """
    like_pattern1 = f"%{trend1_req.industry}%"
    if trend1_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{trend1_req.area}%"
    if trend1_req.area is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{trend1_req.key}%"
    if trend1_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{trend1_req.theme}%"
    if trend1_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2, like_pattern3, like_pattern4))
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
    year,
    SUM(authorization_num) AS authorization_num,
    SUM(apply_num) AS apply_num,
    CASE
        WHEN SUM(apply_num) = 0 THEN 0
        ELSE SUM(authorization_num) / NULLIF(SUM(apply_num), 0)
    END AS proportion
FROM (
    SELECT
        YEAR(application_date) AS year,
        CASE WHEN legal_status IN ('授权', '有效') THEN 1 ELSE 0 END AS authorization_num,
        CASE WHEN legal_status NOT IN ('授权', '有效') THEN 1 ELSE 0 END AS apply_num
    FROM
        biz_patent_0713
    WHERE
        YEAR(application_date) BETWEEN 2014 AND 2024
      AND meta_class LIKE %s
      AND application_area_code LIKE %s
      AND summary LIKE %s
      AND title LIKE %s
) AS yearly_data
GROUP BY
    year
ORDER BY
    year
LIMIT 5;
    """
    like_pattern1 = f"%{trend2_req.industry}%"
    if trend2_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{trend2_req.area}%"
    if trend2_req.area is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{trend2_req.key}%"
    if trend2_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{trend2_req.theme}%"
    if trend2_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2, like_pattern3, like_pattern4))
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
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_concentration(body):  # noqa: E501
    """集中度分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: ConcentrationRes
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400

    body = request.get_json()
    concentration_req = ConcentrationReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
    WITH RecentYears AS (
    SELECT
        applicant_name,
        YEAR(application_date) AS year,
        application_area_code,
        patent_type,
        COUNT(*) AS total_applications
    FROM
        biz_patent_0713
    WHERE
        application_date >= DATE_SUB(CURDATE(), INTERVAL 10 YEAR)
    AND meta_class like %s
    AND application_area_code like %s
    AND summary like %s
    AND title like %s
    GROUP BY
        applicant_name, YEAR(application_date), application_area_code, patent_type
),

     RankedApplicants AS (
         SELECT
             applicant_name,
             year,
             application_area_code,
             patent_type,
             total_applications,
             RANK() OVER (PARTITION BY year, application_area_code, patent_type ORDER BY total_applications DESC) AS rnk
         FROM
             RecentYears
     ),

     Top10Applicants AS (
         SELECT
             year,
             application_area_code,
             patent_type,
             applicant_name,
             total_applications
         FROM
             RankedApplicants
         WHERE
             rnk <= 10
     ),

     TotalApplicationsPerYear AS (
         SELECT
             year,
             application_area_code,
             patent_type,
             SUM(total_applications) AS total_applications_per_year
         FROM
             RecentYears
         GROUP BY
             year, application_area_code, patent_type
     ),

     Top10TotalApplicationsPerYear AS (
         SELECT
             year,
             application_area_code,
             patent_type,
             SUM(total_applications) AS top10_total_applications_per_year
         FROM
             Top10Applicants
         GROUP BY
             year, application_area_code, patent_type
     )

SELECT
    t1.year,
    SUM(t2.top10_total_applications_per_year) / SUM(t1.total_applications_per_year) * 100 AS proportion
FROM
    TotalApplicationsPerYear t1
        JOIN
    Top10TotalApplicationsPerYear t2
    ON
        t1.year = t2.year
            AND t1.application_area_code = t2.application_area_code
            AND t1.patent_type = t2.patent_type
GROUP BY
    t1.year
ORDER BY
    t1.year
LIMIT 5;
    """
    like_pattern1 = f"%{concentration_req.industry}%"
    if concentration_req.industry is None:
        like_pattern1 = f"%%"
    like_pattern2 = f"%{concentration_req.area}%"
    if concentration_req.area is None:
        like_pattern2 = f"%%"
    like_pattern3 = f"%{concentration_req.key}%"
    if concentration_req.key is None:
        like_pattern3 = f"%%"
    like_pattern4 = f"%{concentration_req.theme}%"
    if concentration_req.theme is None:
        like_pattern4 = f"%%"
    cursor.execute(query, (like_pattern1, like_pattern2,like_pattern3,like_pattern4))
    results = cursor.fetchall()
    close_connection(connection)

    if results:
        response = {
            'data': [{'year': row['year'], 'proportion': row['proportion']} for row in results]
        }
        response_json = json.dumps(response, ensure_ascii=False, cls=DecimalEncoder)
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200


def patent_technology(body):  # noqa: E501
    """技术构成分析

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: TechnologyRes
    """
    if not request.is_json:
        return jsonify({'message': 'Invalid input'}), 400

    body = request.get_json()
    technology_req = TechnologyReq.from_dict(body)

    connection = create_connection()
    if connection is None:
        return jsonify({'message': 'Database connection failed'}), 500

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
        return make_response(response_json, 200, {'Content-Type': 'application/json'})
    else:
        return jsonify({'message': 'No data found'}), 200
