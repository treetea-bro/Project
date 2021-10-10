import os
import tkinter as tk
from tkinter import font as tkfont
import tkinter.messagebox as msgbox
from tkinter import *
import numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from WebScraping import WebScraping
import cx_Oracle
import csv
import DataRefine
import PIL
import re


class Tkinter:
    def __init__(self, refine, identity, super_name):
        # 데이터 조작화면에서 넘어올 때 indentity의 값으로 Tkinter_two를 던진다.
        if identity == "Tkinter_two":
            refine.destroy()  # 데이터 조작화면 Tk객체를 받아서 destroy 시킨다.

        self.__super_name = super_name
        self.__search_txt = ""
        self.__start_date = ""
        self.__end_date = ""

        dsn = cx_Oracle.makedsn("localhost", 1521, 'xe')
        self.__db = cx_Oracle.connect('SCOTT', 'TIGER', dsn)
        self.__cur = self.__db.cursor()

        if identity == "Tkinter_one":
            self.__Tkinter_one()
        else:
            self.__Tkinter_two()

    def __Tkinter_one(self):
        self.root = Tk()

        title_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        label = tk.Label(self.root, text="크롤링", font=title_font)
        label.pack(side="top", fill="x", pady=25)

        # UI 입력라벨
        label1 = tk.Label(self.root, text="검색   : ")
        label1.place(x=10, y=90, width=130, height=50)
        label2 = tk.Label(self.root, text="기간   : ")
        label2.place(x=10, y=185, width=130, height=50)
        label2_sub = tk.Label(self.root, text="-제외 숫자 8자리만 입력해주세요. (ex: 20210607)", fg='#0059b3')
        label2_sub.place(x=100, y=230)
        label3 = tk.Label(self.root, text="이름   : ")
        label3.place(x=10, y=280, width=130, height=50)
        label3_sub = tk.Label(self.root, text="이름은 csv파일명, 이미지폴더명, DB테이블명으로 사용됩니다.", fg='#0059b3')
        label3_sub.place(x=50, y=320)
        label4 = tk.Label(self.root, text="~")
        label4.place(x=182, y=182, width=130, height=50)


        self.__sv_super_name_box = StringVar()
        self.__sv_super_name_box.trace("w", lambda name, index, mode,
                                                   buffer=self.__sv_super_name_box: self.__Entry_value_changed(
            self.__sv_super_name_box, "super_name"))
        super_name_box = tk.Entry(self.root, textvariable=self.__sv_super_name_box, width=37)
        super_name_box.insert(0, self.__super_name)
        super_name_box.place(x=115, y=295)

        sv_search_box = tk.StringVar()
        sv_search_box.trace("w",
                            lambda name, index, mode, buffer=sv_search_box: self.__Entry_value_changed(sv_search_box,
                                                                                                       "search_txt"))
        # 검색창
        search_box = tk.Entry(self.root, textvariable=sv_search_box, width=37)
        search_box.place(x=115, y=105)

        # 기간 입력창1
        sv_date_box1 = tk.StringVar()
        sv_date_box1.trace("w", lambda name, index, mode, buffer=sv_date_box1: self.__Entry_value_changed(sv_date_box1,
                                                                                                          "start_date"))
        date_box1 = tk.Entry(self.root, textvariable=sv_date_box1, width=17)
        date_box1.place(x=115, y=200)
        # 기간 입력창2
        sv_date_box2 = tk.StringVar()
        sv_date_box2.trace("w", lambda name, index, mode, buffer=sv_date_box2: self.__Entry_value_changed(sv_date_box2,
                                                                                                          "end_date"))
        date_box2 = tk.Entry(self.root, textvariable=sv_date_box2, width=17)
        date_box2.place(x=255, y=200)

        button1 = tk.Button(self.root, text="이미지 크롤링", width=23, height=5, command=self.__Image_btn)
        button2 = tk.Button(self.root, text="텍스트 크롤링", width=23, height=5, command=self.__Text_btn)
        button3 = tk.Button(self.root, text="데이터 조작화면으로 이동", width=23, height=2, command=self.__Root_destory_one)
        button5 = tk.Button(self.root, width=23, height=2, text="프로그램 종료", command=self.__Exit_yesno)
        button1.place(x=420, y=100)
        button2.place(x=420, y=205)
        button3.place(x=420, y=320)
        button5.place(x=420, y=370)

        self.root.title("크롤링")
        self.root.iconbitmap("icon/data_server_icon.ico")
        self.root.geometry("600x420")
        self.root.resizable(False, False)
        self.root.mainloop()

    def __Entry_value_changed(self, buffer, identity):
        if identity == "super_name":
            self.__super_name = buffer.get()
        elif identity == "search_txt":
            self.__search_txt = buffer.get()
        elif identity == "start_date":
            self.__start_date = buffer.get()
        else:
            self.__end_date = buffer.get()

    def __Image_btn(self):
        # 날짜 입력 유효성검사 부분
        if self.__date_pattern_check():
            web_scraping = WebScraping(self.__super_name, self.__search_txt, self.__start_date, self.__end_date)
            # 중복 이름의 csv파일이 존재할 경우, 확인 메시지에서 확인을 누르면 True를 반환하고, 아닐경우 False를 반환한다.
            if web_scraping.naver_image():
                self.__Root_destory_one()

    def __Text_btn(self):
        # 날짜 입력 유효성검사 부분
        if self.__date_pattern_check():
            web_scraping = WebScraping(self.__super_name, self.__search_txt, self.__start_date, self.__end_date)
            # 중복 이름의 csv파일이 존재할 경우, 확인 메시지에서 확인을 누르면 True를 반환하고, 아닐경우 False를 반환한다.
            if web_scraping.naver_knowledge_in():
                self.__Root_destory_one()

    def __date_pattern_check(self):
        if len(self.__start_date) == 0 or len(self.__end_date) == 0:
            msgbox.showerror(message="기간을 입력하여 주세요.")
            return False
        elif len(self.__start_date) != 8 or len(self.__end_date) != 8 \
                or not self.__start_date.isdigit() or not self.__end_date.isdigit():
            msgbox.showerror(message="기간을 잘못 입력하셨습니다. \n 양식에 맞게 다시 입력해주세요.")
            return False
        elif self.__super_name == "":
            msgbox.showerror(message="이름을 입력하여 주세요.")
        elif len(self.__super_name) is not len(self.__super_name.replace(" ", "")):
            msgbox.showerror(message="이름에서 공백을 제거하여 주세요.")
            return False
        else:
            return True

    def __Exit_yesno(self):
        response = msgbox.askyesno("프로그램 종료", message="프로그램을 종료하시겠습니까?")
        if response == 1:  # 네,OK
            quit()

    def __Root_destory_one(self):
        self.root.destroy()
        self.__Tkinter_two()

    def __Root_destory_two(self):
        self.root.destroy()
        self.__Tkinter_one()

    def __Tkinter_two(self):
        self.root = Tk()

        title_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        label = Label(self.root, text="데이터 조작 화면", font=title_font)
        label.pack(side="top", fill="x", pady=10)

        # UI 기본라벨
        lable4 = Label(self.root, text="이름   : ")
        lable4.place(x=80, y=100, width=130, height=50)

        self.__sv_super_name_box = StringVar()
        self.__sv_super_name_box.trace("w", lambda name, index, mode,
                                                   buffer=self.__sv_super_name_box: self.__Entry_value_changed(
            self.__sv_super_name_box, "super_name"))
        super_name_box = tk.Entry(self.root, textvariable=self.__sv_super_name_box, width=35)
        super_name_box.insert(0, self.__super_name)
        super_name_box.place(x=190, y=115)

        # 버튼
        button1 = Button(self.root, text="워드 클라우드로 보기", width=20, height=5, command=self.__Word_Cloud_btn)  # 워드클라우드 함수
        button2 = Button(self.root, text="이미지 확인하기", width=20, height=5, command=self.__Image_watch_btn)  # 이미지 확인하는 함수
        button3 = Button(self.root, text="DB에 저장하기", width=20, height=5, command=self.__Data_save_btn)  # DB에 저장하는 함수
        button4 = Button(self.root, text="데이터 정제", width=20, height=5, command=self.__DataRefine_btn)  # 데이저 정제화면 이동
        button5 = Button(self.root, text="돌아가기", width=13, height=2, command=self.__Root_destory_two)  # 처음 PAGE로 돌아가기
        button1.place(x=100, y=190)
        button2.place(x=100, y=300)
        button3.place(x=300, y=190)
        button4.place(x=300, y=300)
        button5.place(x=475, y=355)

        self.root.title("데이터 조작")
        self.root.iconbitmap("icon/data_server_icon.ico")
        self.root.geometry("600x420")
        self.root.resizable(False, False)
        self.root.mainloop()

    def __DataRefine_btn(self):
        if self.__super_name.strip() == '':
            msgbox.showerror(message="이름을 입력해주세요.")
        elif len(self.__super_name.strip()) is not len(self.__super_name.strip().replace(' ', '')):
            msgbox.showerror(message="이름에서 공백을 제거하여 주세요.")
        else:
            file_path = self.__file_path()
            if file_path is None:
                return
            # 파일이 존재하지만 DB에 테이블이 생성 안되있으면 에러메시지와 함께 리턴한다.
            self.__cur.execute("SELECT COUNT(*) FROM ALL_TABLES WHERE TABLE_NAME = '" + self.__super_name.upper() + "'")
            if self.__cur.fetchone()[0] == 0:
                if msgbox.showerror(message="해당 이름의 테이블이 없습니다. 우선 DB에 저장하기 버튼을 눌러주세요."):
                    return

            DataRefine.DataRefine(self.root, file_path, self.__super_name)

    def __file_path(self):
        current_path = ""
        img_path = "Image_Text/" + self.__super_name + ".csv"
        knowledge_path = "Knowledge_Text/" + self.__super_name + ".csv"
        if os.path.exists(img_path):
            current_path = img_path
        elif os.path.exists(knowledge_path):
            current_path = knowledge_path
        else:
            msgbox.showerror(message="해당 이름의 csv파일이 존재하지 않습니다.")
            return None

        return current_path

    def __Word_Cloud_btn(self):
        if self.__super_name.strip() == '':
            msgbox.showerror(message="이름을 입력해주세요.")
        elif len(self.__super_name.strip()) is not len(self.__super_name.strip().replace(' ', '')):
            msgbox.showerror(message="이름에서 공백을 제거하여 주세요.")
        else:
            path = self.__file_path()
            if path is not None:
                text = open(path, encoding='utf-8').read()
                font_path = 'C:/Windows/Fonts/malgun.ttf'
                alice_mask = np.array(PIL.Image.open("icon/alice_mask.png"))
                text = re.sub('[a-zA-Z]', ' ', text)
                wc = WordCloud(font_path=font_path, background_color="white", max_words=200, max_font_size=200,
                               width=800,
                               height=500,  mask=alice_mask).generate(text)
                plt.figure(figsize=(7, 7))
                plt.imshow(wc)
                plt.tight_layout(pad=0.5)
                plt.axis('off')
                plt.show()

                path = "Refined_File/"
                if not os.path.exists(path):
                    os.makedirs(path)
                wc.to_file(path + "wordcloud_result.png")

    def __Data_save_btn(self):
        if self.__super_name.strip() == '':
            msgbox.showerror(message="이름을 입력해주세요.")
        elif len(self.__super_name.strip()) is not len(self.__super_name.strip().replace(' ', '')):
            msgbox.showerror(message="이름에서 공백을 제거하여 주세요.")
        else:
            # 테이블 생성 및 데이터 입력
            self.__Create_table()

    def __Image_watch_btn(self):
        image_path = "image/" + self.__super_name

        if self.__super_name.strip() == '':
            msgbox.showerror(message="이름을 입력해주세요.")
        elif len(self.__super_name.strip()) is not len(self.__super_name.strip().replace(' ', '')):
            msgbox.showerror(message="이름에서 공백을 제거하여 주세요.")
        elif not os.path.exists(image_path):
            msgbox.showerror(message="해당이름의 이미지 폴더가 존재하지 않습니다.")
            return
        else:
            # 테이블 생성 및 데이터 입력
            new_window = Toplevel()
            new_window.geometry("600x600+850+150")
            new_window.title("image file ")
            new_window.resizable(False, False)

            file_list = os.listdir("image/" + self.__super_name + "/")
            image_len = len(file_list)

            if image_len > 0:
                pass
            else:
                msgbox.showerror("이미지가 없습니다.")

            all_img = []
            for i in range(image_len):
                all_img.append(PIL.ImageTk.PhotoImage(
                    PIL.Image.open("image/" + self.__super_name + "/" + self.__super_name + "_" + str(i) + ".png")))

            label_img = Label(new_window, width=600, height=540, bg='white', image=all_img[0])
            label_img.pack()

            global num
            num = 0

            def forward_image():
                global num
                num = num - 1
                label_img.configure(image=all_img[num])
                if num < 1:
                    buttonExample.config(state=DISABLED)
                else:
                    buttonExample1.config(state=NORMAL)

            def next_image():
                global num
                num = num + 1
                label_img.configure(image=all_img[num])
                if num > len(file_list) - 2:
                    buttonExample1.config(state=DISABLED)
                else:
                    buttonExample.config(state=NORMAL)

            # 이미지 이동버튼
            buttonExample = Button(new_window, width=5, height=2, text="이전", command=forward_image)
            buttonExample1 = Button(new_window, width=5, height=2, text="다음", command=next_image)
            buttonExample.place(x=250, y=550)
            buttonExample1.place(x=310, y=550)

    def __Create_table(self):
        self.__cur.execute("SELECT COUNT(*) FROM ALL_TABLES WHERE TABLE_NAME = '" + self.__super_name.upper() + "'")
        if self.__cur.fetchone()[0] == 1:
            if msgbox.askyesno("확인", "같은 테이블명이 이미 존재합니다. 기존의 테이블을 삭제하고 새로 만드시겠습니까?"):
                query = "DROP TABLE " + self.__super_name
                self.__cur.execute(query)
            else:
                return

        path = self.__file_path()
        if path is not None:
            f = open(path, 'r', encoding='utf-8')
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
            self.__Insert(path)
            msgbox.showinfo(message="저장 완료")

    def __Insert(self, path):
        f = open(path, 'r', encoding='utf-8')
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
