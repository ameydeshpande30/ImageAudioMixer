from flask import Flask, jsonify, render_template, request, redirect, url_for
from werkzeug import secure_filename
import os, shutil, threading
from datetime import datetime


app = Flask(__name__)
inputFilePath = "inputs/"
outputFilePath = "outputs/"
app.config['UPLOAD_FOLDER'] = inputFilePath
data = {}
def clenUP():
    try:
        shutil.rmtree(outputFilePath)
    except:
        pass
    try:
        shutil.rmtree(inputFilePath)
    except:
        pass
    try:
        os.mkdir(outputFilePath)
    except:
        pass
    try:
        os.mkdir(inputFilePath)
    except:
        pass


def mergeData(inputImage, inputAudio, outputfilename, event):
    inputImage = inputFilePath + inputImage
    inputAudio = inputFilePath + inputAudio
    outputfilename = outputFilePath + outputfilename
    cmd = "ffmpeg -loop 1 -i {} -i {} -c:v libx264 -tune stillimage -strict experimental -c:a aac -b:a 192k -pix_fmt yuv420p  -shortest {}".format(inputImage, inputAudio, outputfilename)
    os.system(cmd)
    event.set()

def start_func(inputImage, inputAudio, outputfilename):
    event = threading.Event()
    t1 = threading.Thread( target=mergeData,args=(inputImage, inputAudio, outputfilename, event) )
    t1.start()
    return event

@app.route('/')
def upload_file():
   return render_template('upload.html')
	
@app.route('/', methods = ['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        global data
        outputCode = str((datetime.now()-datetime(1970,1,1)).total_seconds())
        fI = request.files['image']
        inputImage = outputCode + fI.filename
        fI.save(inputFilePath + secure_filename(inputImage))
        fA = request.files['audio']
        inputAudio = outputCode + fA.filename
        fA.save(inputFilePath + secure_filename(inputAudio))
        event = start_func(inputImage, inputAudio, outputCode + ".mp4")
        data[outputCode] = event
        # return 'file uploaded successfully' + outputCode
        return redirect ("/wait/" + outputCode)
    else:
        return render_template('upload.html')

@app.route("/wait/<code>")
def waitTime(code):
    try:
        event = data[code]
        if event.isSet():
            return "done"
        else:
            return "Please refresh again to see"

    except:
        return 'Not Found'


@app.route("/api")
def test():
    now = datetime.now()
    date_time = (now-datetime(1970,1,1)).total_seconds()
    name = str(date_time) + ".mp4"
    start_func('testImage.jpeg', 'testAudio.m4a', name)
    return jsonify({"uid" : name})


if __name__ == '__main__':
    clenUP()
    app.run(debug=True)