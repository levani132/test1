from flask import Flask, render_template, request, jsonify
import json
import psycopg2
import os
import pytesseract
from PIL import Image
import jwt
from datetime import datetime, timedelta
from functools import wraps






pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
key = 'parting'

def loginRequired(f):
	@wraps(f)
	def decoratedFunction(*args, **kwargs):
		try:
			decoded = jwt.decode(request.headers.get('Authorization'), key, algorithms='HS256')
			print(decoded)
			datetimeObject = datetime.strptime(decoded['endDate'], '%Y-%m-%d %H:%M:%S.%f')
			print(datetimeObject)
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




if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	my_port = str(port)
	app.run(host='0.0.0.0', port=my_port)