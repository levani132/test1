from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET']) 
def foo():
    data = {"test":23} #request.json
    return jsonify(data)

#app.run(host="0.0.0.0", port=5000)
app.run()

#test = {"test_key":1000}
#print (jsonify(test)) 