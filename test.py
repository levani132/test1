import flask
app = flask.Flask(__name__)

@app.route("/")
def index():
    response_value_1=1
    response_value_2="Test"
    return flask.jsonify(key1=response_value_1,key2=response_value_2)

app.run()


#test = {"test_key":1000}
#print (jsonify(test)) 