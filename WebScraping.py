import os
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
from tkinter import messagebox
import shutil
import re


class WebScraping:
    def __init__(self, super_name, search_txt, start_date, end_date):
        self.__super_name = super_name
        self.__search_txt = search_txt
        self.__start_date = start_date
        self.__end_date = end_date

    def naver_image(self):
        same_name_img = "Image_Text/" + self.__super_name + ".csv"
        same_name_knowledge = "Knowledge_Text/" + self.__super_name + ".csv"
        if os.path.exists(same_name_img) or os.path.exists(same_name_knowledge):
            if messagebox.askyesno("확인", "같은 csv파일명이 이미 존재합니다. 기존 파일을 삭제하고 새로 만드시겠습니까?"):
                if os.path.exists(same_name_img):
                    os.remove(same_name_img)
                if os.path.exists(same_name_knowledge):
                    os.remove(same_name_knowledge)
            else:
                return False

        # 브라우저를 실행하고, 네이버 이미지 주소에다가 파라메터로 기간 정보를 넣은 url을 브라우저에 전달한다.
        start_date = re.sub("-", "", self.__start_date)
        end_date = re.sub("-", "", self.__end_date)
        binary = 'c:/chromedriver/chromedriver.exe'
        browser = webdriver.Chrome(binary)
        list_url = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=" + str(
            self.__search_txt) + "&res_fr=0&res_to=0&sm=tab_opt&color=&ccl=0&nso=so%3Ar%2Cp%3Afrom" + str(
            start_date) + "to" + str(end_date) + "&recent=0&datetype=6&startdate=" + str(
            start_date) + "&enddate=" + str(end_date) + "&gif=0&optStr=d&nso_open=1"
        browser.get(list_url)

        # 브라우저가 안정될때까지 3초 여유를 주고, 이미지정보를 더 가져오기위해 end를 5번 더 눌러준다.
        time.sleep(3)
        for i in range(5):
            browser.find_element_by_xpath("//body").send_keys(Keys.END)
            time.sleep(2)

        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")

        # 이미지 파일을 담을 폴더를 생성하고 해당 폴더에 검색된 이미지들을 넣는다.
        self.__img_file(soup)

        browser.quit()
        return True

    def __img_file(self, soup):
        # 이미지 파일의 소스 페이지를 리스트 변수에 담는다.
        file_path = []
        for link in soup.find_all("img", class_="_image _listImage"):
            try:
                file_path.append(link.get("src"))
            except KeyError:
                continue

        file_blog_path = []
        for link in soup.find_all("a", target="_blank"):
            try:
                file_blog_path.append(link.get("href"))
            except KeyError:
                continue

        # 해당경로에 해당 이름의 폴더가 존재하는지 확인하고, 해당 이름의 폴더가 존재하지 않는경우 생성해준다.
        img_path = "image/" + self.__super_name + "/"

        if os.path.exists(img_path):
            shutil.rmtree(img_path)
            os.makedirs(img_path)
        else:
            os.makedirs(img_path)

        txt_path = "Image_Text"
        if not os.path.exists(txt_path):
            os.makedirs(txt_path)

        # 변수에 담은 이미지파일 소스페이지에서 이미지를 긁어다가 폴더에 넣어준다.
        f = open(txt_path + "/" + self.__super_name + ".csv", "w", encoding='utf-8')
        f.write("FILE_NAME, PATH, FILE_BLOG, FILE_URL\n")
        for i, p in enumerate(file_path):
            file_name = self.__super_name + "_" + str(i) + ".png"
            urllib.request.urlretrieve(p, img_path + file_name)
            f.write("'" + file_name + "', '" + img_path + "', '" + file_blog_path[i] + "', '" + p + "'\n")

    def naver_knowledge_in(self):
        same_name_img = "Image_Text/" + self.__super_name + ".csv"
        same_name_knowledge = "Knowledge_Text/" + self.__super_name + ".csv"
        if os.path.exists(same_name_img) or os.path.exists(same_name_knowledge):
            if messagebox.askyesno("확인", "같은 csv파일명이 이미 존재합니다. 기존 파일을 삭제하고 새로 만드시겠습니까?"):
                if os.path.exists(same_name_img):
                    os.remove(same_name_img)
                if os.path.exists(same_name_knowledge):
                    os.remove(same_name_knowledge)
            else:
                return False

        # 브라우저를 실행하고, 네이버 지식인 주소에다가 파라메터로 기간 정보를 넣은 url을 브라우저에 전달한다.
        start_date = re.sub("-", "", self.__start_date)
        end_date = re.sub("-", "", self.__end_date)
        binary = 'c:/chromedriver/chromedriver.exe'
        browser = webdriver.Chrome(binary)
        list_url = ("https://search.naver.com/search.naver?where=kin&query=" +
                    str(self.__search_txt) + "&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom" +
                    str(start_date) + "to" + str(end_date) + "&sm=tab_opt&answer=0&kin_start=1")
        browser.get(list_url)
        time.sleep(3)

        # 페이지를 넘겨가면서 리스트 변수에 게시글의 제목 + 내용을 담는다.
        titles = []
        contents = []
        apply_times = []
        urls = []
        while True:
            html = browser.page_source
            soup = BeautifulSoup(html, "lxml")
            titles_search = soup.find_all("a", class_="api_txt_lines question_text")
            contents_search = soup.find_all("a", class_="api_txt_lines answer_text")
            apply_times_search = soup.find_all("span", class_="desc")
            for title, content, apply_time in zip(titles_search, contents_search, apply_times_search):
                title_ = title.get_text()
                content_ = content.get_text()
                apply_time_ = apply_time.get_text()
                url = title.get("href")
                try:
                    titles.append(title_)
                    contents.append(content_)
                    apply_times.append(apply_time_)
                    urls.append(url)
                except KeyError:
                    continue

            browser.find_element_by_css_selector("div.api_sc_page_wrap > div > a.btn_next").click()
            break_point = soup.find("a", class_="btn_next")
            if break_point.get('aria-disabled') == "true":
                break

        txt_path = "Knowledge_Text"
        if not os.path.exists(txt_path):
            os.makedirs(txt_path)

        f = open(txt_path + "/" + self.__super_name + ".csv", "w", encoding='utf-8')
        f.write("REG_DATE, TITLE, CONTENT, URL\n")
        for apply_time, title, content, urls in zip(apply_times, titles, contents, urls):
            f.write("'" + apply_time.replace('.', '') + "', '" + title.replace('\'', '')
                    + "', '" + content.replace('\'', '') + "', '" + urls.replace('\'', '') + "'\n")
        f.close()

        browser.quit()
        return True
