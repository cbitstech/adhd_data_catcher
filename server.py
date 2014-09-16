# Liberally taken from Test Server in https://github.com/cbitstech/Purple-Robot (GPL v3).
import cherrypy
import hashlib
import os
import time
import pandas
import zipfile
import requests

from json import loads, dumps

CONFIG = {
    'global': {
        'server.socket_port': 9080,
        'server.socket_host': '0.0.0.0'
    }
}

with open('mailgun_api') as f:
    JSS_MAILGUN_TOKEN = f.read().strip()

class RobotPost:
    def index(self, json=None):
        json_obj = loads(json)

        payload_str = json_obj['Payload']

        m = hashlib.md5()
        m.update(json_obj['UserHash'] + json_obj['Operation'] + json_obj['Payload'])

        checksum_str = m.hexdigest()

        result = {}
        result['Status'] = 'error'
        result['Payload'] = "{}"

        if checksum_str == json_obj['Checksum']:
            result['Status'] = 'success'

            timestamp = str(time.time())

            # Output!
            path = 'files' + os.sep + json_obj['UserHash'] + os.sep + timestamp
            self.dump_data(json_obj['UserHash'], path)

        m = hashlib.md5()
        m.update(result['Status'] + result['Payload'])

        result['Checksum'] = m.hexdigest()

        cherrypy.response.headers['Content-Type']= 'application/json'

        return dumps(result, indent=2)

    def dump_data(self, user_hash, stem):

            d = os.path.dirname(stem)
            if not os.path.exists(d):
                os.makedirs(d)
            f = open('%.json' % stem, 'w')
            f.write(dumps(json_obj, indent=2))
            f.close()

            data = pandas.read_json(json_obj, typ='series')
            data.to_frame().to_excel('%.xsl' % stem, 'w')
            data.to_csv('%s.csv' % stem)
            f = open('%s.txt' % stem, 'w')
            f.write(data.to_string())
            f.close()

    def email_data(self, user_hash, stem):

        pass

    index.exposed = True

cherrypy.quickstart(RobotPost(), config=CONFIG)
