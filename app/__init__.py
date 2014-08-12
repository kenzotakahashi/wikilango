from flask import Flask
from pymongo import MongoClient
import os
# from flask.ext.pymongo import PyMongo
from flask_sslify import SSLify
import logging
from logging import StreamHandler

app = Flask(__name__)

# Format: MONGOHQ_URL: mongodb://<user>:<pass>@<base_url>:<port>/<url_path>
if os.environ.get('MONGOHQ_URL'):
    client = MongoClient(os.environ['MONGOHQ_URL'])
    db = client.app28410175
else:
    client = MongoClient()
    db = client.wikilango


file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

app.config.from_object('config')

# mongo = PyMongo(app)
# sslify = SSLify(app)

from app import views