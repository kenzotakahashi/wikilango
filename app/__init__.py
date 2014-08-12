from flask import Flask
from pymongo import MongoClient
import os
# from flask.ext.pymongo import PyMongo
from flask_sslify import SSLify

# Format: MONGOHQ_URL: mongodb://<user>:<pass>@<base_url>:<port>/<url_path>
if os.environ.get('MONGOHQ_URL'):
    client = MongoClient(os.environ['MONGOHQ_URL'])
else:
    client = MongoClient()


app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = client.wikilango
# mongo = PyMongo(app)
# sslify = SSLify(app)

from app import views