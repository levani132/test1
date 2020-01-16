from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET']) 
def foo():
    data = {"test":23} #request.json
    return jsonify(data)

app.run(port=80)


#test = {"test_key":1000}
#print (jsonify(test)) 