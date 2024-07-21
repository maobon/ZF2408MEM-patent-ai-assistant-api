from flask import make_response


def make_cors_response(response_data, status_code=200):
    if response_data == '':
        response = make_response(response_data, status_code)
    else:
        response = make_response(response_data, status_code, {'Content-Type': 'application/json'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, POST,GET'
    return response
