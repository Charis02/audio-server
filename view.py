from flask import Flask,request,render_template,send_file,Response
import pymongo
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
import io
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import sys

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
        cur_date = datetime.datetime.utcnow()
        date = datetime.datetime(cur_date.year,cur_date.month,cur_date.day,0,0,0)

        for f in files:
            db = get_db()
        
            if allowed_file(f.filename):
                new_audio = {"name": f.filename,"contents": f.read(),
                "date_added": date,
                "filetype":get_filetype(f.filename),
                "filesize":f.tell()} # create object to store in db
                new_id = db.files.insert_one(new_audio).inserted_id
                result.append('File ' + f.filename + ' uploaded successfully. Unique id: ' + str(new_id) + '<br>')
            else:
                result.append('Filetype not allowed for file ' + f.filename + '<br>')
            
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
        
        try:
            file_id = ObjectId(request.form['id'])
            file_data = db.files.find_one({"_id": file_id})
        except:
            return 'Invalid id'
            
        if file_data is not None:
            f = io.BytesIO(file_data['contents'])    
        
            return send_file(f,download_name=file_data['name'],last_modified=file_data['date_added'],as_attachment=True)
        else:
            return 'File with id {} was not found!'.format(file_id)
        
    return render_template('get.html')

@app.route('/plot.png')
def add_hist_image():
    """
    Create histogram image and return it as a response
    at /plot.png
    """
    db = get_db()

    histogram_pipeline = [{"$match":{"date_added":{"$gte":datetime.datetime.utcnow() - datetime.timedelta(days=7)}}},{"$group":{"_id":"$date_added","cnt":{"$sum":1}}},{"$sort":{"_id":1}}]
    histogram_raw = db.files.aggregate(histogram_pipeline)
    histogram_x = []
    histogram_y = []

    for h in histogram_raw:
        histogram_x.append(h['_id'].strftime('%Y-%m-%d'))
        histogram_y.append(h['cnt'])

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    output = io.BytesIO()
    axis.bar(histogram_x,histogram_y)
    FigureCanvas(fig).print_png(output)
    
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/stats')
def stats():
    """
    Renders stats page with 

    formats: Top 10 file formats
    average: Average file size
    histogram: Histogram of last 7 days uploads
    """
    db = get_db()

    ## Top 10 file formats
    
    format_pipeline = [{"$group":{"_id":"$filetype","cnt":{"$sum":1}}},{"$sort":{"cnt":-1}},{"$limit":10}]
    formats_raw = db.files.aggregate(format_pipeline)
    formats = []

    for f in formats_raw:
        formats.append(f['_id'] + ': ' + str(f['cnt']) + '<br>')

    ## Average file size

    average_pipeline = [{"$group":{"_id":"null","avg": {"$avg":"$filesize"}}}]
    average_raw = db.files.aggregate(average_pipeline)
    average = 0

    for av in average_raw:
        average = av['avg']

    ## Histogram of last 7 days uploads


    return render_template('stats.html', formats=''.join(formats), average=average)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)