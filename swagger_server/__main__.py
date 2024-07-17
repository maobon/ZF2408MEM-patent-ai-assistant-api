#!/usr/bin/env python3

import connexion
from job.sync_patent_to_dify import SyncPatentToDify

from swagger_server import encoder
def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    # scheduler = SyncPatentToDify(app)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'API Demo'}, pythonic_params=True)
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
