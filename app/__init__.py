from flask import Flask
from pymongo import MongoClient
# from flask.ext.pymongo import PyMongo

from flask_sslify import SSLify

app = Flask(__name__)
app.config.from_object('config')
client = MongoClient()
db = client.wikilango
# mongo = PyMongo(app)
# sslify = SSLify(app)

from app import views