# -*- coding: utf-8 -*-
import json
from pymongo import MongoClient

mongo_connect = MongoClient("localhost", 27017)
db = mongo_connect.Final

try:
    with open("mongoDB_Collection_board.txt", "r") as f:
        for v in f.read().split("\n"):
            json_object = json.loads(v)
            db.board.insert_one(json_object)
    with open("mongoDB_Collection_analysis.txt", "r") as f:
        for v in f.read().split("\n"):
            json_object = json.loads(v)
            db.analysis.insert_one(json_object)
except Exception as e:
    print(e)
