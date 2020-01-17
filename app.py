from flask import Flask, request, jsonify
import os

app = Flask(__name__)
port = int(os.environ.get('PORT', 17995)) 
@app.route('/', methods=['GET']) 
def foo():
    data = {"test":23} #request.json
    return jsonify(data)
app.run(host="0.0.0.0", port=5000)
#app.run( port=port)

#test = {"test_key":1000}
#print (jsonify(test)) 


#