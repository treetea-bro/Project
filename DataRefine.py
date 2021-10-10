import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import cx_Oracle
import csv
from PIL import ImageTk, Image
import Tkinter


class DataRefine:
    def __init__(self, Tkinter_root, file_path, super_name):
        Tkinter_root.destroy()
        self.__super_name = super_name

        dsn = cx_Oracle.makedsn("localhost", 1521, 'xe')
        self.__db = cx_Oracle.connect('SCOTT', 'TIGER', dsn)
        self.__cur = self.__db.cursor()

        self.__root = Tk()

        # tkinter의 GUI가 총 4개의 Frame 안에 구성되어있다.
        self.__Frame_one(file_path)
        self.__Frame_two()
        self.__Frame_three()
        self.__Frame_four()

        # tkinter창 관련 설정
        self.__root.title("데이터 정제")
        self.__root.iconbitmap("icon/data_server_icon.ico")
        self.__root.geometry("1200x700")
        self.__root.resizable(False, False)
        self.__root.mainloop()

    def __Frame_one(self, file_path):
        f = open(file_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        # csv파일의 첫번째 row를 headers 변수에 담는다. (컬럼(헤더)정보)
        headers = next(csv_reader)
        # rowid 값을 tkinter 첫번째 컬럼에 넣어주고 해당 부분을 hide할 것이기 때문에, 파일에 존재하지 않는 rowid 정보를 미리 넣어준다.
        cnt = [1]
        # 위 변수는 컬럼인덱스를 의미하고, 현재 변수는 컬럼이름을 의미한다.
        self.__column_names = ["ROWID"]

        # 각각 변수에 컬럼인덱스 값과 컬럼이름을 담아준다.
        enum_cnt = 2
        for i, j in enumerate(headers):
            cnt.append(enum_cnt + i)
            self.__column_names.append(j.replace(' ', ''))

        # 첫번째 frame 선언부
        frame1 = LabelFrame(self.__root)
        frame1.pack(fill="both", expand="yes", padx=10, pady=2)

        # 트리뷰 생성 및 스타일을 지정한다.
        self.__trv = ttk.Treeview(frame1, columns=cnt, height="9")
        style = ttk.Style(self.__trv)
        style.configure("Treeview", rowheight=30)

        # 트리뷰 안에서 사용할 이미지를 태그 부분에 바인딩한다.
        self.im_checked = ImageTk.PhotoImage(Image.open("icon/checked.png"))
        self.im_unchecked = ImageTk.PhotoImage(Image.open("icon/unchecked.png"))
        self.__trv.tag_configure('checked', image=self.im_checked)
        self.__trv.tag_configure('unchecked', image=self.im_unchecked)

        # 트리뷰의 위치를 지정한다.
        self.__trv.pack(side=LEFT)
        self.__trv.place(x=0, y=0)

        # 트리뷰의 컬럼(헤더)부분에 파일에서 읽어온 컬럼(헤더)정보를 넣어준다.
        for i, j in enumerate(self.__column_names):
            self.__trv.heading(i + 1, text=j)

        # 체크박스 이미지부분의 컬럼(헤더)이름과 너비를 조절한다.
        self.__trv.heading('#0', text='')
        self.__trv.column('#0', width=50)

        # 첫번째 인덱스에 넣어놓은 rowid부분을 hide 시킨다.
        exclusionlist = [1]  # 여기에 들어간 컬럼의 인덱스는 숨겨져서 값은 존재하지만, UI에는 표시되지 않게된다.
        displaycolumns = []
        for col in self.__trv["columns"]:
            if not int(col) in exclusionlist:
                displaycolumns.append(col)
        self.__trv["displaycolumns"] = displaycolumns

        # 트리뷰를 클릭하면 발생하는 이벤트를 Select_row 함수에 바인드 시켜준다.
        self.__trv.bind('<Button-1>', self.__Select_row)

        # 세로축 스크롤바
        yscrollbar = ttk.Scrollbar(frame1, orient="vertical", command=self.__trv.yview)
        yscrollbar.pack(side=RIGHT, fill="y")

        # 가로축 스크롤바
        xscrollbar = ttk.Scrollbar(frame1, orient="horizontal", command=self.__trv.xview)
        xscrollbar.pack(side=BOTTOM, fill="x")

        # 스크롤바 선택부분 UI를 제대로 동작하게 한다.
        self.__trv.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        # 트리뷰에 슈퍼네임과 같은 이름의 테이블 데이터를 넣어준다.
        self.__Treeview_init()

    def __Frame_two(self):
        # 두번째 frame 선언부
        frame2 = LabelFrame(self.__root)
        frame2.pack(fill="both", padx=10, pady=2)

        # 콤보박스
        sql = "SELECT COLUMN_NAME FROM COLS WHERE TABLE_NAME = '" + self.__super_name + "'"  # 해당 테이블의 컬럼명을 알아낸다.
        self.__cur.execute(sql)
        columns = self.__cur.fetchall()
        self.__combo = ttk.Combobox(frame2, state="readonly", width=30)
        self.__combo['values'] = columns  # 콤보박스에다가 컬럼명들을 넣어준다.
        self.__combo.pack(side=tk.LEFT, padx=3)
        self.__combo.current(0)  # 컬럼명 중 첫번째를 콤보박스에 처음으로 보여준다.
        self.__combo.bind("<<ComboboxSelected>>", self.__Combo_changed)  # 콤보박스 값 변경 이벤트를 Combobox_changed 함수에 바인딩한다.
        self.__combo_selected = self.__column_names[1]

        # 라벨, 엔트리, 버튼들
        lbl = Label(frame2, text="검색어 입력 :")
        lbl.pack(side=tk.LEFT, padx=3)
        self.__frame2_entry_text = StringVar()
        frame2_entry = Entry(frame2, textvariable=self.__frame2_entry_text)
        frame2_entry.pack(side=tk.LEFT, padx=3)
        search_btn = Button(frame2, text="검색", command=self.__Search)
        search_btn.pack(side=tk.LEFT, padx=3)
        delete_btn = Button(frame2, text="삭제", command=self.__Delete_row)
        delete_btn.pack(side=tk.RIGHT, padx=3)
        update_btn = Button(frame2, text="업데이트", command=self.__Update_row)
        update_btn.pack(side=tk.RIGHT, padx=3)

    def __Frame_three(self):
        # 3번째 Frame 선언부
        frame3 = Frame(self.__root)
        frame3.pack(fill="both", expand="yes", padx=10, pady=2)
        self.__frame3_scrollbar = ScrolledText(frame3, height=0)
        self.__frame3_scrollbar.pack(side=tk.LEFT, fill="both", expand="yes")

    def __Frame_four(self):
        # 4번째 Frame 선언부
        frame4 = Frame(self.__root)
        frame4.pack(fill="both", padx=10, pady=2)
        go_back_btn = Button(frame4, text="데이터 조작으로 이동", command=self.__Tkinter_destroy)
        go_back_btn.pack(side=tk.RIGHT, padx=3)

    def __Tkinter_destroy(self):
        Tkinter.Tkinter(self.__root, "Tkinter_two", self.__super_name)

    def __Treeview_write(self, rows):
        # 기존에 존재하는 트리뷰 안의 내용을 다 삭제하고 새로 받은 데이터를 넣어준다.
        self.__trv.delete(*self.__trv.get_children())
        for i in rows:
            self.__trv.insert('', 'end', values=i, tags="unchecked")

    def __Treeview_init(self):
        query = "SELECT ROWID, A.* FROM " + self.__super_name + " A"
        self.__cur.execute(query)
        rows = self.__cur.fetchall()
        self.__Treeview_write(rows)

    def __Search(self):
        text = self.__frame2_entry_text.get()
        query = "SELECT ROWID, A.* FROM " + self.__super_name + " A " \
                                                                "WHERE " + self.__combo_selected + " LIKE '%" + text + "%'"
        self.__cur.execute(query)
        rows = self.__cur.fetchall()
        self.__Treeview_write(rows)

    def __Update_row(self):
        # scrollbar에서 값을 가져온다.
        text = self.__frame3_scrollbar.get("1.0", tk.END)

        if messagebox.askyesno("확인", "입력하신 정보로 선택된 행의 콤보박스에 선택된 컬럼 값을 업데이트 하시겠습니까?"):
            query = "UPDATE " + self.__super_name + " SET " + self.__combo_selected + " = '" + text + "'" \
                                                                                                      " WHERE ROWID = '" + self.__rowid + "'"
            self.__cur.execute(query)
            self.__db.commit()
            self.__Treeview_init()

    def __Delete_row(self):
        if messagebox.askyesno("확인", "선택된 행의 정보를 삭제하시겠습니까?"):
            query = "DELETE FROM " + self.__super_name + " WHERE ROWID = '" + self.__rowid + "'"
            self.__cur.execute(query)
            self.__db.commit()
            self.__Treeview_init()

    def __Combo_changed(self, event):
        # 콤보박스 값이 변경될때마다 새로 변수에 담아준다.
        self.__combo_selected = self.__combo.get()

    def __Select_row(self, event):
        # 모든 행의 체크박스 이미지를 unchecked로 바꾸어준다.
        for i in self.__trv.get_children():
            self.__trv.item(i, tags="unchecked")

        # 클릭한 행의 체크박스 이미지를 checked로 바꾸어 준다.
        rowid = self.__trv.identify_row(event.y)  # rowid는 오라클의 rowid가 아니라 tkinter에서 제공하는 해당 row의 고유번호를 의미한다.
        self.__trv.item(rowid, tags="checked")

        # tkinter의 rowid를 변수로 이용해 트리뷰 안의 해당 row의 정보를 가져온다.
        row_info = self.__trv.set(rowid)
        # 컬럼인덱스 1에다가 숨겨놓은 오라클의 rowid를 가져온다.
        self.__rowid = row_info["1"]
        # 현재 선택된 콤보박스의 컬럼명을 가지고 해당 컬럼의 인덱스 정보를 가져온다.
        index = self.__column_names.index(self.__combo_selected)

        # 기존의 scrollbar안의 텍스트를 삭제하고, 새로 선택된 행의 콤보박스에 선택된 컬럼의 값을 scrollbar에 넣어준다.
        self.__frame3_scrollbar.delete('1.0', END)
        self.__frame3_scrollbar.insert(tk.INSERT, row_info[str(index + 1)])

    def __del__(self):
        self.__cur.close()
        self.__db.close()
