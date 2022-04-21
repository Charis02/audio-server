from flask import Flask,request,render_template
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/audio_db"
mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/upload', methods=['GET','POST'])
def upload():
    """
    Input: file or batch of files
    Returns: unique id or list of unique ids

    Stores files in a directory
    """
    if request.method == 'POST':
        f = request.files['file']
        f.save('/tmp/' + f.filename)
        return 'File uploaded successfully'
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)