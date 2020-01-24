from flask import Flask, render_template, request, jsonify
import json
import psycopg2
import os
import pytesseract
from PIL import Image
import jwt
from datetime import datetime, timedelta
from functools import wraps
import numpy as np
import cv2
import pytesseract
import re
import base64
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, jsonify
import json
import psycopg2
import os
import io

from google.cloud import vision
client = vision.ImageAnnotatorClient()


def log(msg):
    connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                port = "5432",
                                database = "dedn9b8htmngg7")
    cursor = connection.cursor()
    sqlText = '''INSERT INTO parking.logs (data) VALUES ((%s));'''
    cursor.execute(sqlText,[str(msg)])
    connection.commit()
    cursor.close()
    connection.close()


pytesseract.pytesseract.tesseract_cmd = r'/app/.apt/usr/bin/tesseract'
key = 'parting'

def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        try:
            decoded = jwt.decode(request.headers.get('Authorization'), key, algorithms='HS256')
            datetimeObject = datetime.strptime(decoded['endDate'], '%Y-%m-%d %H:%M:%S.%f')
            if (datetimeObject + timedelta(days=30)) < datetime.today():
                raise NameError('Token expired!')
            return f(*args, **kwargs)
        except Exception as e:
            cols = ('error',)
            rows = (str(e),)
            result = []
            result.append(dict(zip(cols,rows)))
            return json.dumps(result[0])
    return decoratedFunction


app = Flask(__name__)
#os.getenv(PORT,'8800')
#os.getenv(IP, '0.0.0.0')

@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        dato = request.json
        print('dato', dato)
        print(dato['ID'])
        ##print(type(dato))
        connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                              password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                              host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                              port = "5432",
                              database = "dedn9b8htmngg7")

        cursor = connection.cursor()
        text = '''INSERT INTO mobile VALUES ((%s), (%s),999);'''
        cursor.execute(text,(dato['ID'],dato['MODEL']))
        connection.commit()
        columns = ('ID','MODEL')
        temp = dato['ID']
        cursor.execute("select * from mobile where id = (%s)", [temp])
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns,row)))
        #sel = cursor.fetchone()
        #zaza = json.dumps(sel)
        return json.dumps(result[0])

@app.route('/auth', methods = ['POST'])
def auth():
    if request.method == 'POST':
        dato = request.json

        connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                      password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                      host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                      port = "5432",
                                      database = "dedn9b8htmngg7")
        cursor = connection.cursor()
        text = 'select phone_number from parking.users where phone_number = (%s);'
        cursor.execute(text, [dato['phoneNumber']])
        sel = cursor.fetchall()
        errorCode = ''
        if sel == []:
            errorCode = 'ნომერი არ არის რეგისტრირებული.'
            encoded = ''
        else:        
            encoded = jwt.encode({'phoneNumber': sel[0], 'endDate':str(datetime.today())}, key, algorithm='HS256').decode("utf-8")
        cols = ('token','error')
        rows = (encoded,errorCode)
        result = []
        result.append(dict(zip(cols,rows))) 
        return json.dumps(result[0])

@app.route('/getLoginStatus', methods = ['POST'])
@loginRequired
def getLoginStatus():
    if request.method == 'POST':
        cols = ('isAuthenticated',)
        rows = (True,)
        result = []
        result.append(dict(zip(cols,rows)))
        return json.dumps(result[0]) 

@app.route('/register', methods = ['POST'])
def register():
    errorText = None
    encoded = ''
    try:        
        dato = request.json
        connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                    password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                    host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                    port = "5432",
                                    database = "dedn9b8htmngg7")
        cursor = connection.cursor()
        text = "select 1 from parking.users where phone_number = (%s);"
        cursor.execute(text,[dato['phoneNumber']])
        zaza = cursor.fetchone()
        if zaza != None:
            raise NameError('ტელეფონის ნომერი დარეგისტრირებულია')
        text = "select 1 from parking.cars where car_number = (%s);"
        cursor.execute(text,[dato['carNumber']])
        zaza = cursor.fetchone()
        if zaza != None:
            raise NameError('მანქანის ნომერი დარეგისტრირებულია')
        text  = '''INSERT INTO parking.users (name,phone_number) VALUES ((%s), (%s));'''
        cursor.execute(text,[dato['name'],dato['phoneNumber']])
        #connection.commit()
        text = "select id from parking.users where phone_number = (%s);"
        cursor.execute(text, [dato['phoneNumber']])
        userId = cursor.fetchone()
        text = '''INSERT INTO parking.cars (user_id,car_number) VALUES ((%s), (%s));'''
        cursor.execute(text,[userId[0],dato['carNumber']])
        connection.commit()
        encoded = jwt.encode({'phoneNumber': dato['phoneNumber'], 'endDate':str(datetime.today())}, key, algorithm='HS256').decode("utf-8")
    except Exception as e:
        errorText = str(e)
    finally:
        cursor.close()
        connection.close()
        cols = ('token','error')
        rows = (encoded,errorText)
        result = []
        result.append(dict(zip(cols,rows))) 
        return json.dumps(result[0])

@app.route('/scan', methods = ['POST'])
#@loginRequired
def scan():
    try:
        if request.method == 'POST':
            data = request.json
            content = base64.b64decode(data['base64'].replace('\n', ''))
            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)

            texts = [t.description in response.text_annotations]
            p = re.compile('.*([A-Z][A-Z]-[0-9][0-9][0-9]-[A-Z][A-Z])(.*)')
            text = filter(lambda text: p.fullmatch(text))[0]
            # pil_image = Image.open(BytesIO())
            # im = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            # opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            # grayImage = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
            # (thresh, img) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
            # y,x = img.shape
            # b=200
            # img = cv2.rotate(img[int(y/2-3*x/32):int(y/2-50+3*x/32),int(x/2+b-3*x/8):int(x/2-b+3*x/8)], cv2.ROTATE_90_CLOCKWISE)
            # text = pytesseract.image_to_string(img)

            #p = re.compile('.*([A-Z][A-Z]-[0-9][0-9][0-9]-[A-Z][A-Z])(.*)')
            #m = p.match(text)
            connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                        password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                        host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                        port = "5432",
                                        database = "dedn9b8htmngg7")
            cursor = connection.cursor()
            sqlText = '''INSERT INTO parking.logs (data) VALUES ((%s));'''
            cursor.execute(sqlText,[str(data['base64'])])
            connection.commit()
            cursor.close()
            connection.close()
            return(json.dumps({ 'text': text }))
    except Exception as e:
        connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                    password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                    host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                    port = "5432",
                                    database = "dedn9b8htmngg7")
        cursor = connection.cursor()
        sqlText = '''INSERT INTO parking.logs (data) VALUES ((%s));'''
        cursor.execute(sqlText,[str(e)])
        connection.commit()
        cursor.close()
        connection.close()
        return(json.dumps({"error":str(e)}))
    
@app.route('/search', methods = ['POST'])
@loginRequired
def search():
    errorText = None
    try:        
        dato = request.json
        connection = psycopg2.connect(user = "vukyhtaqmatqpj",
                                    password = "2cf5b5c6b3b7d7e99f02ddc474088225a0015c93996b515194872873f96f65b4",
                                    host = "ec2-54-228-237-40.eu-west-1.compute.amazonaws.com",
                                    port = "5432",
                                    database = "dedn9b8htmngg7")
        cursor = connection.cursor()
        text = "select name,phone_number from parking.users where id = (select user_id from parking.cars where car_number = (%s));"
        cursor.execute(text,[dato['carNumber']])
        zaza = cursor.fetchone()
        if zaza == None:
            raise NameError('მანქანის ნომერი არ მოიძებნა')
    except Exception as e:
        cursor.close()
        connection.close()
        errorText = str(e)
        return (json.dumps({'name':'','phoneNumber':'','error': errorText}))
    else:
        cursor.close()
        connection.close()
        #print(cursor.fetchall())
        return (json.dumps({'name':zaza[0],'phoneNumber':zaza[1],'error': errorText}))
        
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    my_port = str(port)
    app.run(host='0.0.0.0', port=my_port)