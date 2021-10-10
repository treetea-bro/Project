import os
import re
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class WebScraping:
    __search_txt = ""
    __start_date = ""
    __end_date = ""

    def WebScrapingTool(self):
        global __search_txt
        global __start_date
        global __end_date

        __search_txt = input("검색할 내용은 : ")
        # 기간을 입력받고, 기간 양식이 틀리게 입력되면 다시 입력받는다.
        while True:
            try:
                start_date, end_date = input("기간 (ex: 2020-11-01 ~ 2021-01-23) : ").split("~")
            except ValueError as e:
                print("기간 양식을 예제와 같이 맞춰주세요.")
                continue

            __start_date = start_date.strip()
            __end_date = end_date.strip()
            regex = re.compile(r'(\d{4})-(\d{2}-\d{2})')
            start_dt_chk = regex.search(__start_date)
            end_dt_chk = regex.search(__end_date)
            if start_dt_chk is None or end_dt_chk is None or len(__start_date) != 10 or len(__end_date) != 10:
                print("기간 양식을 예제와 같이 맞춰주세요.")
            else:
                break

        # 입력받은 값이 1이거나 2면 값에 해당하는 메소드를 실행시키고, 그 외의 경우 다시 입력받는다.
        while True:
            re_value = input("1.이미지 / 2.txt : ")
            if re_value.strip() == '1':
                self.__naver_image()
                break
            elif re_value.strip() == '2':
                self.__naver_knowledge_in()
                break
            else:
                print("1이나 2만 입력해주세요.")

    def __naver_image(self):
        global __search_txt
        global __start_date
        global __end_date
        # 브라우저를 실행하고, 네이버 이미지 주소에다가 파라메터로 기간 정보를 넣은 url을 브라우저에 전달한다.
        start_date = re.sub("-", "", __start_date)
        end_date = re.sub("-", "", __end_date)
        binary = 'c:/chromedriver/chromedriver.exe'
        browser = webdriver.Chrome(binary)
        list_url = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=" + str(
            __search_txt) + "&res_fr=0&res_to=0&sm=tab_opt&color=&ccl=0&nso=so%3Ar%2Cp%3Afrom" + str(
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

        print("\n- {} ~ {} 사이에 검색된 네이버 이미지 타이틀과 개수 - \n".format(__start_date, __end_date))
        # 이미지 파일을 담을 폴더를 생성하고 해당 폴더에 검색된 이미지들을 넣는다.
        self.__img_file(soup)
        # 이미지들의 게시글 제목을 파일에 write하고, 콘솔에 출력한다.
        self.__img_text(soup)

        # 이미지들의 개수를 구한 다음 콘솔에 출력한다.
        image_count = len(browser.find_elements_by_css_selector("._image._listImage"))
        print("\n- 가져온 image의 개수 - : ", image_count)

        # 콘솔에 출력한 텍스트에 대한 WordCloud를 볼지 안볼지를 물어보고 입력값을 받는다.
        while True:
            res = input("\n\n검색된 내용을 WordCloud로 보시겠습니까? Y/N : ")
            if res.upper() == "Y":
                self.__word_cloud("image.txt")
                return
            elif res.upper() == "N":
                return

    def __img_file(self, soup):
        # 해당경로에 해당 이름의 폴더가 존재하는지 확인하고, 해당 이름의 폴더가 존재하지 않는경우 생성해준다.
        if not os.path.exists("image") :
            os.makedirs("image")
        # 이미지 파일의 소스 페이지를 리스트 변수에 담는다.
        params = []
        for link in soup.find_all("img", class_="_image _listImage"):
            try:
                params.append(link.get("src"))
            except KeyError:
                continue
        # 변수에 담은 이미지파일 소스페이지에서 이미지를 긁어다가 폴더에 넣어준다.
        for idx, p in enumerate(params):
            urllib.request.urlretrieve(p, "C:/img/" + str(idx) + "_naver.jpg")

            '''img_num = 1
                   while True:
                       try:
                           imgList = browser.find_element_by_xpath(
                               '// *[ @ id = "main_pack"] / section / div / div[1] / div[1] / div[' + str(
                                   img_num) + '] / div / div[1] / a / img')
                           src = imgList.get_attribute('src')
                           urllib.request.urlretrieve(src, "c:/img/" + str(img_num) + "_naver.jpg")
                       except NoSuchElementException:
                           break
                       img_num += 1'''  # 이미지 추출방법 1

    def __img_text(self, soup):
        # 이미지를 사용한 해당 홈페이지의 제목을 리스트 변수에 담는다.
        params = []
        for link in soup.find_all("a", class_="text"):
            try:
                params.append(link.get("title"))
            except KeyError:
                continue
        # 이미지를 사용한 해당 홈페이지의 제목을 어절 단위로 img.txt 파일에 write하고, 콘솔에는 문장 단위로 출력한다.
        with open("image.txt", "w", encoding='utf-8') as f:
            for phrase in params:
                words = phrase.split()
                for word in words:
                    f.write(word + "\n")
                print(phrase)

    def __naver_knowledge_in(self):
        global __search_txt
        global __start_date
        global __end_date

        # 브라우저를 실행하고, 네이버 지식인 주소에다가 파라메터로 기간 정보를 넣은 url을 브라우저에 전달한다.
        start_date = re.sub("-", "", __start_date)
        end_date = re.sub("-", "", __end_date)
        binary = 'c:/chromedriver/chromedriver.exe'
        browser = webdriver.Chrome(binary)
        list_url = ("https://search.naver.com/search.naver?where=kin&query=" +
                    str(__search_txt) + "&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom" +
                    str(start_date) + "to" + str(end_date) + "&sm=tab_opt&answer=0&kin_start=1")
        browser.get(list_url)
        time.sleep(3)

        print("\n- {} ~ {} 사이에 검색된 네이버 지식인 내용들 - \n".format(__start_date, __end_date))

        # 페이지를 넘겨가면서 리스트 변수에 게시글의 제목 + 내용을 담는다.
        params = []
        roof = True
        while roof:
            html = browser.page_source
            soup = BeautifulSoup(html, "lxml")
            web_list01 = soup.find_all("a", class_="api_txt_lines question_text")
            web_list02 = soup.find_all("a", class_="api_txt_lines answer_text")
            for title, contents in zip(web_list01, web_list02):
                post = "지식인 제목 : " + title.get_text() + "\n      답변 : " + contents.get_text()
                if post in params:
                    roof = False
                    break
                try:
                    params.append(post)
                except KeyError:
                    continue
            browser.find_element_by_css_selector("div.api_sc_page_wrap > div > a.btn_next").click()

        # 리스트 변수에 담은 값들을 text.txt 파일에 write + 콘솔에 출력하기
        f = open("text.txt", "w", encoding='utf-8')
        for i in params:
            f.write(i + "\n")
            print(i)
        f.close()

        # 콘솔에 출력한 텍스트에 대한 WordCloud를 볼지 안볼지를 물어보고 입력값을 받는다.
        while True:
            res = input("\n\n검색된 내용을 WordCloud로 보시겠습니까? Y/N : ")
            if res.upper() == "Y":
                self.__word_cloud("text.txt")
                return
            elif res.upper() == "N":
                return

    def __word_cloud(self, file_name):
        text = open(file_name, encoding='utf-8').read()

        font_path = 'C:/Windows/Fonts/malgun.ttf'

        alice_mask = np.array(Image.open("C://alice_mask.png"))

        stwords = set(STOPWORDS)  # 기본적으로 많이 쓰는 단어 제외할 단어
        stwords.add("지식인"), stwords.add("답변"), stwords.add("제목")

        wc = WordCloud(font_path=font_path, background_color="white", max_words=200, max_font_size=200, width=800,
                       height=500, stopwords=stwords, mask=alice_mask).generate(text)
        plt.figure(figsize=(7, 7))
        plt.imshow(wc)
        plt.tight_layout(pad=0.5)
        plt.axis('off')
        plt.show()
        wc.to_file("result_review.png")