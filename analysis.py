# -*- coding: utf-8 -*-
import cv2, pafy
from mongoDB import mongoC
from img_model.src import check
from datetime import datetime, timedelta
import shutil, os
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
from konlpy.tag import Okt
import tensorflow as tf
#from tensorflow.keras.preprocessing.sequence import pad_sequences
#from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

mongo = mongoC()

class analysis:
    def start(self, url):
        self.url = url
        if "http://" or "https://" in url:
            url = url.replace("https://", "")
            url = url.replace("www.", "")

        if "youtube.com/watch?v=" in url:
            # back_id = 유튜브 영상아이디
            back_id = url.replace("youtube.com/watch?v=", "")
        else:
            back_id = url.replace("youtu.be/", "")

        url = "https://www." + url
        try:
            self.information = YouTubeTranscriptApi.get_transcript(back_id,
                                            languages=['ko'])
        except:
            return "script", 0, None, None
        
        self.new_model = tf.keras.models.load_model('Final_Proeject\\static\\models\\emotion_nlp.h5')
        self.labels = ['Happy', 'Embarrassment', 'Angry', 'Sad']
        self.okt = Okt()

        for info in self.information:
            text_emotion = self.text(info["text"])
            info["text_emotion"] = text_emotion

        if not os.path.exists("Final_Proeject\\static\\temp"):
            os.mkdir("Final_Proeject\\static\\temp")
        else:
            shutil.rmtree("Final_Proeject\\static\\temp")
            os.mkdir("Final_Proeject\\static\\temp")
            
        main_emotion = self.image(url)
          
        today = datetime.today()
        max_emotion = max(main_emotion, key=main_emotion.get)
        next_id = mongo.next_id(max_emotion)
        shutil.move("Final_Proeject\\static\\temp", "Final_Proeject\\static\\img\\" + max_emotion + "\\") 
        folder_name = "Final_Proeject\\static\\img\\" + max_emotion + "\\" + str(next_id) + "_" + today.strftime("%Y%m%d")
        os.rename("Final_Proeject\\static\\img\\" + max_emotion + "\\temp", folder_name)   
        
        img__path = "../static/img/" + max_emotion + "/" + str(next_id) + "_" + today.strftime("%Y%m%d") + "/"
        db_img_title_path = img__path + "title.jpg"
        mongo.insert_board(next_id, max_emotion, db_img_title_path, back_id, self.video.title, today.strftime("%Y.%m.%d"))

        mongo.insert_analysis(next_id, max_emotion, today.strftime("%Y.%m.%d"), self.movie_info)
        
        print(max_emotion)
        return "success", next_id, max_emotion, back_id

    def text(self, sentence):
        x_test_2 = pd.Series(
            sentence
        )
        
        x_test_2 = x_test_2.apply(lambda x : self.stopword(x))
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(x_test_2)
        train_sequences_2 = tokenizer.texts_to_sequences(x_test_2)
        train_inputs_2 = pad_sequences(train_sequences_2, maxlen=34, padding='post')
        #나도 조카가 생겨! 너무 기뻐.
        y_predict = self.new_model.predict(train_inputs_2)
        label = self.labels[y_predict[0].argmax()]
        confidence = y_predict[0][y_predict[0].argmax()]
        if confidence in [0.87662035, 0.6139252] and label == "Happy" :
            return "Neutral"
        elif confidence < 0.4:
            return "Neutral"
        else:
            return label
            # print(y_predict, sentence, label, confidence)

    def stopword(self, text):
        clean = []
        for word in self.okt.pos(text, stem=True): #어간 추출
            #if word[1] not in ['Josa', 'Eomi', 'Punctuation']: #조사, 어미, 구두점 제외 
            # if (word[1] not in ['Josa', 'Eomi', 'Punctuation']) and (word[0] not in ['없다', '있다', '같다', '하다', '친구', '너무','않다']):
            #     clean.append(word[0])
            if (word[1] not in ['Josa', 'Eomi', 'Punctuation']) and (word[0] not in ['없다', '있다', '같다', '하다', '친구', '너무','않다','오늘',
                                                                                '되다','요즘','사람','남편','아내','보다', '자꾸', '돼다', '회사', '정말', '우리', '많다', '이제','이번',
                                                                                '학교', '아들', '생각', '결혼', '때문', '엄마', '아빠', '가족', '부모님', '이다', '남자친구', '아이','받다', '나르다',
                                                                                '오다', '자다', '모이다', '먹다', '이렇다', '다니다', '상사', '주변', '점점', '모두', '공부', '이야기', '직장','지금',
                                                                                '나이', '업무', '세상', '취업', '관계', '어리다', '모으다', '나오다', '내다', '해주다','하나', '생활', '얘기', '시간',
                                                                                '대학', '전화', '일이', '의사', '병원', '동료', '자기', '직원', '여자친구', '동생', '마음','전화', '걸다', '매일', '같이',
                                                                                '다른', '나가다', '들다', '연락', '성적', '항상', '자리', '대학', '많이', '크다', '모임', '빌리다','이렇게', '진로',
                                                                                '진짜', '생활', '노인', '후배', '아무', '애가', '나다', '여자', '아침', '남자', '나서다', '건강검진', '보고', '조금',
                                                                                '얘기', '모습', '사이', '근태', '얼마', '운동', '할머니', '계속', '선생님', '오랜', '믿다', '해주다', '생일', '기분', '자주','가다',
                                                                                                                                                                '들','내','나','것','때','이','그']):
                clean.append(word[0])
        return " ".join(clean)

    def image(self, url):
        faceCascade = cv2.CascadeClassifier('Final_Proeject\\img_model\\src\\visualize\\haarcascade_frontalface_alt2.xml') #괄호 안 따옴표 안 경로에서 검출에 필요한xml파일을 불러옴. 'haarcascades'다운로드 해야함. 경로수정은 알아서.
        # url = 'https://www.youtube.com/watch?v=k3owHySExac'

        self.video = pafy.new(url)
        print('title = ', self.video.title) #영상의 제목을 표시.
        best = self.video.getbest(preftype = 'mp4')
        print('best.resolution', best.resolution) #영상의 해상도를 표시.

        cap = cv2.VideoCapture(best.url)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps
        print("영상의 길이 : ", duration, "초")

        second = 0
        increase_width = 0.5
        success = True

        urllib.request.urlretrieve(self.video.getbestthumb(), "Final_Proeject\\static\\temp\\title.jpg")
        main_emotion = {'Angry':0,
                        'Embarrassment':0,
                        'Happy':0,
                        'Sad':0}
        images = []
        self.movie_info = dict()
        highest_pic_emotion = ""
        pic_second = '0'
        max_percent = 0.0
        check.model_load('private_model_134_77.t7')
        for info in self.information:
            start = info['start']
            second = start - increase_width
            end = info['start'] + info['duration']
            while second <= duration:
                second += increase_width
                if start <= second <= end:
                    cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
                    success, image = cap.read()
                    if not success:
                        break
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray)
                    if len(faces) != 0:
                        cv2.imwrite("Final_Proeject\\static\\temp\\%0.1f.jpg" % second, image)
                        print("saved image %0.1f.jpg" % second)
                        images.append({'path': "Final_Proeject\\static\\temp\\%0.1f.jpg" % second})
                        emotion, percent = check.concat_info("Final_Proeject\\static\\temp\\%0.1f.jpg" % second)
                        percent = float(percent)

                        if max_percent < percent:
                            max_percent = percent
                            highest_pic_emotion = emotion
                            pic_second = "%0.1f"% second # 가장 높은 퍼센트일때의 시간 정보

                        if emotion != "Neutral":
                            main_emotion[emotion] += 1
                else:
                    if max_percent > 0.7:
                        H_M_S = int(start)
                        self.movie_info[pic_second] = {"text":info["text"], "text_emotion":info["text_emotion"],
                                                        "pic_emotion":highest_pic_emotion, "H_M_S":str(timedelta(seconds=H_M_S))}
                        max_percent = 0.0
                    break

        check.guided_backprop(images, "private_model_134_77.t7")  

        return main_emotion