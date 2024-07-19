#!/usr/bin/env python3

import connexion
from flask import jsonify

from swagger_server.job.sync_patent_to_dify import SyncPatentToDify
from swagger_server.controllers.create_pdf import createPdf

from swagger_server import encoder
from flask_cors import CORS


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

    app.run(host='0.0.0.0', port=8080)


def _build_cors_preflight_response():
    response = jsonify()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    main()
