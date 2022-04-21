from flask import Flask,request,render_template
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

allowed_types = {'txt','mp3'}

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
        f = request.files['file']
        db = get_db()
    
        if allowed_file(f.filename):
            new_audio = {"name": get_name(f.filename),"contents": f.read()} # create object to store in db
            db.audio.insert_one(new_audio)
            return 'File uploaded successfully'
        else:
            return 'Unsupported file type!'

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)