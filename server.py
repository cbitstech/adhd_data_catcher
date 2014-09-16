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
JSS_MAILGUN_SANDBOX = 'sandbox1ec7b7dbe74d48dab76ffeec5b334da1'
SURVEY_ADDR = "James Spencer <james.s.spencer@gmail.com>"

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
            self.email_data('files', json_obj['UserHash'])
            self.cleanup('files', json_obj['UserHash'])

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

    def email_data(self, file_dir, user_hash):

        # Construct zip file...
        zipf = '%s.zip' % (user_hash,)
        wd = os.getcwd()
        os.chdir(file_dir)
        os.remove(zipf)
        with zipfile.ZipFile(zipf, 'w'):
            for f in os.listdir(user_hash):
                myzip.write(os.path.join(user_hash, f))

        # EMAIL!
        requests.post(
            "https://api.mailgun.net/v2/%s.mailgun.org/messages" % (JSS_MAILGUN_SANDBOX,),
            auth=("api", JSS_MAILGUN_TOKEN),
            data={"from": "5 Men with ADHD <postmaster@%s.mailgun.org>" % (JSS_MAILGUN_SANDBOX,),
              "to": SURVEY_ADDR,
              "subject": "ADHD survey response: %s" % (user_hash,),
              "text": """Please find attached a response to the ADHD survey from user %s.

5 Men with ADHD""" % (user_hash,)}
        )

        os.chdir(wd)

    def cleanup(self, file_dir, user_hash):

        os.chdir(file_dir)
        shutil.rmtree(user_hash)
        os.chdir(wd)

    index.exposed = True

cherrypy.quickstart(RobotPost(), config=CONFIG)
