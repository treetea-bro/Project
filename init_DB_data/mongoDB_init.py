# -*- coding: utf-8 -*-
from pymongo import MongoClient

mongo_connect = MongoClient("localhost", 27017)
db = mongo_connect.Final

try:
    db.board.insert_many()
except Exception as e:
    print(e)
