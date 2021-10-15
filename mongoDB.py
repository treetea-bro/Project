# -*- coding: utf-8 -*-
from pymongo import MongoClient
import math

class mongoC:
    mongo_connect = MongoClient("localhost", 27017)
    db = mongo_connect.Final
    
    def next_id(self, emotion):
        next_id = 1
        for data in self.db.board.find({"emotion":emotion}, {"_id":0, "id":1}).sort("id", -1).limit(1):
            next_id = data["id"] + 1
        return int(next_id)

    def insert_board(self, id, emotion, img_title, url, title, today):
        try:
            self.db.board.insert_one({"id":id, "emotion":emotion, "image":img_title,
             "url":url, "title":title, "date":today})
        except Exception as e:
            print(e)
    
    def insert_analysis(self, id, emotion, today, pic_time):
        try:
            self.db.analysis.insert_one({"id":id, "emotion":emotion, "date":today, "pic_time":pic_time})
        except Exception as e:
            print(e)

    def select_board(self, emotion, page): 
        skip_num = 12 * (int(page) - 1); 
        len = self.db.board.find({"emotion":emotion}).count(); 
        json_data = []    
        for data in self.db.board.find({"emotion":emotion}, {"_id":0}).sort("id", -1).skip(skip_num).limit(12):
            json_data.append(data)
        return json_data, math.ceil(len / 12)

    def select_analysis(self, id, emotion):
        json_data = []
        for data in self.db.analysis.find({"id":id, "emotion":emotion},{"_id":0}):
            json_data.append(data)
        return json_data