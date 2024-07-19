from flask import make_response


def make_cors_response(response_data, status_code=200):
    response = make_response(response_data, status_code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, POST'
    return response
