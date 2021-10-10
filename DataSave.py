import csv
import cx_Oracle
from tkinter import messagebox
import os


class CreateTable:
    def __init__(self, super_name):
        self.__super_name = super_name

        dsn = cx_Oracle.makedsn("localhost", 1521, 'xe')
        self.__db = cx_Oracle.connect('SCOTT', 'TIGER', dsn)
        self.__cur = self.__db.cursor()

        self.__Create_table()

    def __Create_table(self):
        self.__cur.execute("SELECT COUNT(*) FROM ALL_TABLES WHERE TABLE_NAME = '" + self.__super_name.upper() + "'")
        if self.__cur.fetchone()[0] == 1:
            if messagebox.askyesno("확인", "같은 테이블명이 이미 존재합니다. 기존의 테이블을 삭제하고 새로 만드시겠습니까?"):
                query = "DROP TABLE " + self.__super_name
                self.__cur.execute(query)
            else:
                return

        current_path = ""
        img_path = "Image_Text/" + self.__super_name + ".csv"
        knowledge_path = "Knowledge_Text/" + self.__super_name + ".csv"
        if os.path.exists(img_path):
            current_path = img_path
        elif os.path.exists(knowledge_path):
            current_path = knowledge_path

        f = open(current_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        headers = next(csv_reader)
        rows = next(csv_reader)
        header_name = ''
        for header, row in zip(headers, rows):
            if row.strip().isdigit():
                header_name += header + ' NUMBER,'
            else:
                header_name += header + ' VARCHAR2(4000),'
        query = "CREATE TABLE " + self.__super_name + \
                "(" \
                + header_name.rstrip(',') + \
                ")"
        self.__cur.execute(query)
        self.__Insert(current_path)

    def __Insert(self, current_path):
        f = open(current_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        next(csv_reader)  # 컬럼데이터를 빼주기 위해 한번 실행
        for row in csv_reader:
            values = ''
            for i in row:
                values += i + ','

            query = "INSERT INTO " + self.__super_name + " VALUES(" + values.rstrip(',') + ")"
            self.__cur.execute(query)

        f.close()
        self.__db.commit()

    def __del__(self):
        self.__cur.close()
        self.__db.close()
