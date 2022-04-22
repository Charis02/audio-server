from django.shortcuts import render
from flask import Flask,request,render_template,send_file
import pymongo
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
import io

app = Flask(__name__)

allowed_types = {'mp3','m4a','wav','3gp','aa','aac','aax','m4b','msv','ogg','tta','wma','wv','webm'}

def get_db():
    """
    Returns database connection
    """
    client = MongoClient(host='audio_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    db = client["audio_db"]
    return db

@app.route('/')
def hello_world():
    return 'Hello World!'


def get_filetype(filename):
    """
    Returns filetype of file
    """
    return filename.rsplit('.', 1)[1].lower()

def get_name(filename):
    """
    Returns name of file
    """
    return filename.rsplit('.', 1)[0]

def allowed_file(filename):
    """
    Returns true if filetype is allowed
    """
    return '.' in filename and get_filetype(filename) in allowed_types

@app.route('/upload', methods=['GET','POST'])
def upload():
    """
    Input: file or batch of files
    Returns: unique id or list of unique ids

    Stores files in a directory
    """
    if request.method == 'POST':
        result = []
        files = request.files.getlist('file')

        for f in files:
            db = get_db()
        
            if allowed_file(f.filename):
                new_audio = {"name": f.filename,"contents": f.read(),
                "date_added": datetime.datetime.utcnow(),
                "filetype":get_filetype(f.filename),
                "filesize":f.tell()} # create object to store in db
                new_id = db.files.insert_one(new_audio).inserted_id
                result.append('<br> File ' + f.filename + ' uploaded successfully. Unique id: ' + str(new_id) + '</br>')
            else:
                result.append('<br> Filetype not allowed for file ' + f.filename + '</br>')
            
        return render_template('upload.html', result=''.join(result))

    return render_template('upload.html')

@app.route('/get', methods=['GET','POST'])
def get():
    """
    Input: unique id
    Returns: file contents

    Retrieves file from db
    """
    if request.method == 'POST':
        db = get_db()
        file_id = ObjectId(request.form['id'])
        file_data = db.files.find_one({"_id": file_id})

        if file_data is not None:
            f = io.BytesIO(file_data['contents'])    
        
            return send_file(f,download_name=file_data['name'],last_modified=file_data['date_added'],as_attachment=True)
        else:
            return 'File with id {} was not found!'.format(file_id)
        
    return render_template('get.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)