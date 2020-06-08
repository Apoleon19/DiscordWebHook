import json
import logging.config
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.config'))
logger = logging.getLogger('main')


class WebHook:
    def __init__(self, url: str, **kwargs):
        self.hook_url = url

        self.data = kwargs.get('data', dict())
        self.files = kwargs.get('files', dict())

    def add_file(self, filename, file):
        self.files[f'_{filename}'] = file

    def add_files(self, files):
        self.files.update(files)

    def send(self):
        try:
            if bool(self.files) is True:
                if len(self.files) > 10:
                    raise Exception('Cannot send more then 10 files per request')
                self.files["payload_json"] = (None, json.dumps(self.data))
                r = requests.post(url=self.hook_url, files=self.files)
            elif bool(self.data) is True:
                r = requests.post(url=self.hook_url, data=json.dumps(self.data),
                                  headers={'Content-Type': 'application/json'})
            else:
                raise Exception('Cannot send an empty message')
            r.raise_for_status()
            return r
        except Exception as e:
            logger.error(e)
