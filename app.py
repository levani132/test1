from flask import Flask, render_template, request, jsonify
import json
import psycopg2
import os

app = Flask(__name__)
#os.getenv(PORT,'8800')
#os.getenv(IP, '0.0.0.0')
@app.route('/submit', methods = ['POST'])
def submit():
	v_res= [{"a": 1, "b": 2}, {"a": 4, "b": 6}]
	if request.method == 'POST':
		dato = request.json
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
		#result = []
		#for row in cursor.fetchone():
		#	result.append(dict(zip(columns,row)))
		sel = cursor.fetchone()
		#zaza = json.dumps(sel)
		return json.dumps(sel)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	my_port = str(port)
	app.run(host='0.0.0.0', port=my_port)