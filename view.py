from flask import Flask,request,render_template
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/audio_db"
mongo = PyMongo(app)

allowed_types = {'txt'}

@app.route('/')
def hello_world():
    return 'Hello World!'


def get_filetype(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and get_filetype(filename) in allowed_types

@app.route('/upload', methods=['GET','POST'])
def upload():
    """
    Input: file or batch of files
    Returns: unique id or list of unique ids

    Stores files in a directory
    """
    if request.method == 'POST':
        f = request.files['file']
        
        if allowed_file(f.filename):
            return 'File uploaded successfully'
        else:
            return 'Unsupported file type!'
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)