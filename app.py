from flask import Flask, render_template, request
from mongoDB import mongoC
from analysis import analysis

app = Flask(__name__)
mongo = mongoC()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/board')
def classification():
    emotion = request.args.get("emotion")
    page = request.args.get("page")
    json_data, page_len = mongo.select_board(emotion, page)
    return render_template('board.html', emo=emotion, contents=json_data, page_len=page_len)

@app.route("/loader", methods=['POST'])
def loader():
    index_url = request.form
    return render_template("loader.html", url=index_url["url"])

@app.route("/result", methods=['GET', 'POST'])
def result():
    state = "success"
    loader_url = request.form
    
    if loader_url:
        state, id, emotion, url = analysis().start(loader_url["url"])
    else:
        id = request.args.get("id") 
        emotion = request.args.get("emotion")
        url = request.args.get("url")
        if not id or not emotion or not url:
            return render_template('result.html', state="address", data=None, url=None)

    data = mongo.select_analysis(int(id), emotion)
    return render_template('result.html', state=state, data=data, url=url)


if __name__ =="__main__" :
    app.run(debug=False)
