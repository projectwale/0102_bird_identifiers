# from dataclasses import replace
from flask import *
from werkzeug.utils import secure_filename
# from flask import Flask, render_template, request
import pickle
import pymysql
import pandas as pd
import socket
from datetime import datetime
import numpy as np
import tensorflow
from keras.preprocessing import image
from keras.models import load_model
import warnings
warnings.filterwarnings("ignore")
import pickle

app = Flask(__name__)

global usrname
usrname = ""

def dbConnection():
    try:
        connection = pymysql.connect(host="localhost", user="root", password="root", database="dbroadpotholes",charset='utf8')
        return connection
    except:
        print("Something went wrong in database Connection")

def dbClose():
    try:
        dbConnection().close()
    except:
        print("Something went wrong in Close DB Connection")

con=dbConnection()
cursor=con.cursor()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'random string'

print("[info] Model loading....")
# test_model = load_model("birdClassify37.hp5")
image_size=224
print("model loaded successfully!!")
##########################################################################################################
#                                           Register
##########################################################################################################
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        # print("hii register")
        email = request.form['Email']
        password = request.form['pass1']
        username = request.form['Name']

        print(email,password,username)

        try: 
            con = dbConnection()
            cursor = con.cursor()
            sql1 = "INSERT INTO birduser (name, email, password) VALUES (%s, %s, %s)"
            val1 = (username, email, password)
            cursor.execute(sql1, val1)
            print("query 1 submitted")
            con.commit()
            dbClose()

            FinalMsg = "Congrats! Your account registerd successfully!"
        except:
            con.rollback()
            msg = "Database Error occured"
            print(msg)
            return render_template("login.html", error=msg)
        finally:
            dbClose()
        return render_template("login.html",FinalMsg=FinalMsg)
    return render_template("register.html")
##########################################################################################################
#                                               Login
##########################################################################################################
@app.route("/", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password'] 

        print(email,password)

        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute('SELECT * FROM tblregister WHERE email = %s AND password = %s', (email, password))
        result = cursor.fetchone()
        dbClose()
        print("result")
        print(result)
        if result_count>0:
            print("len of result")
            session['uname'] = result[1]
            session['userid'] = result[0]

            global usrname
            usrname += session.get("uname")
            return redirect(url_for('root'))
        else:
            return render_template('login.html')
    return render_template('login.html')
##########################################################################################################
#                                       Product Description
##########################################################################################################
import os
import IPython.display as ipd
import librosa.display
import random
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras.preprocessing import image
import requests
import pandas as pd
from bs4 import BeautifulSoup

# link for extract html data
def getdata(url):
    r = requests.get(url)
    return r.text

@app.route("/recording", methods = ['POST', 'GET'])
def recording():
    global usrname

    # if 'uname' in session:
    print("GET")
    print(session.get("uname"))
    
    if request.method == 'POST':
        global usrname

        print("POST")
        f2 = request.files['file']
        print("audio file")
        print(f2)

        filename_secure = secure_filename(f2.filename)

        f2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_secure))
        print(filename_secure)


        img_path = "static/uploads/"+filename_secure

        BIRDS = ['ABBOTTS BOOBY',
                'ABYSSINIAN GROUND HORNBILL',
                'AFRICAN PIED HORNBILL',
                'AFRICAN PYGMY GOOSE',
                'ALEXANDRINE PARAKEET',
                'AMERICAN AVOCET',
                'AMERICAN BITTERN',
                'AMERICAN FLAMINGO',
                'AMERICAN PIPIT',
                'AMERICAN WIGEON',
                'ASHY STORM PETREL',
                'ASIAN GREEN BEE EATER',
                'AUCKLAND SHAQ',
                'AUSTRALASIAN FIGBIRD',
                'AZARAS SPINETAIL',
                'BALD EAGLE',
                'BANDED BROADBILL',
                'BAR-TAILED GODWIT',
                'CHIPPING SPARROW',
                'CROW',
                'INDIAN PITTA',
                'KING EIDER',
                'RUFOUS KINGFISHER',
                'SNOWY OWL',
                'STEAMER DUCK']

        img = image.load_img(img_path,target_size=(image_size, image_size))
        x = image.img_to_array(img)
        img_4d=x.reshape(1,224,224,3)
        
        prediction = test_model.predict(img_4d)
        new_pred=np.argmax(prediction[0])
        predicted_name = BIRDS[new_pred]
        print("Predicted Image Name: "+str(BIRDS[new_pred]))
        print("---------------------------------------------------------")

        htmldata = getdata("https://animalia.bio/"+str(BIRDS[new_pred]).lower().replace(" ","-"))
        # htmldata = getdata("https://animalia.bio/king-eider")
        soup = BeautifulSoup(htmldata, 'html.parser')
        datas = ''
        heading_s = []
        bird_info = []
        appear_info = []
        for data in soup.find_all("div", {"class": "s-char-kinds__attr"}):
            # print(data.get_text().replace("\n"," ").split())
            data1 = data.get_text().replace("\n","")
            heading_s.append(data1)
        print()
        
        for data in soup.find_all("a", {"class": "s-char-kinds__name"}):
            # print(data.get_text().replace("\n"," "))
            bird_info.append(data.get_text().replace("\n"," "))
        print()
        
        for data in soup.find_all("div", {"class": "s-appearance-block"}):
        #     print(data.get_text())
            # print(" ".join(data.get_text().replace("Show More","").replace("Show Less","").split()))
            appear_info.append(" ".join(data.get_text().replace("Show More","").replace("Show Less","").split()))

        flst = zip(heading_s,bird_info)
        return render_template('services1.html',appear_info=appear_info, flst=flst)
    return render_template('services.html')
##########################################################################################################
#                                               about
##########################################################################################################
@app.route("/about", methods = ['POST', 'GET'])
def about():
    username=session.get('uname')
    return render_template('about.html')
##########################################################################################################
#                                               contact
##########################################################################################################
@app.route("/contact", methods = ['POST', 'GET'])
def contact():
    username=session.get('uname')
    return render_template('contact.html',firstName=username)
##########################################################################################################
#                                               contact
##########################################################################################################
@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    session.pop('uname',None)
    session.pop('userid',None)
    return redirect(url_for('login'))
#########################################################################################################
#                                       Home page
##########################################################################################################
@app.route("/root")
def root():
    global usrname
    if 'uname' in session:
        global usrname

        usrNamed1 = session.get("uname")
        usrNamed2 = session.get('uname')

        print("session name")
        print(usrNamed1)
        print(usrNamed2)

        # con = dbConnection()
        # cursor = con.cursor()
        # sql1 = "SELECT * from pred_bird where username=%s"
        # val1 = (usrNamed2)
        # cursor.execute(sql1, val1)
        # res = cursor.fetchall()
        # result = list(res)
        # dbClose()

        # usrId = [i[0] for i in result]
        # userName = [i[1] for i in result]
        # birdName = ["../"+i[2] for i in result]
        # filePath = [i[3] for i in result]

        # print("bird name list")
        # print(birdName)

        # all_lst = zip(birdName, filePath)
        return render_template('index.html')



if __name__=='__main__':
    app.run(debug=True)
    # app.run('0.0.0.0')