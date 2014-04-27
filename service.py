import os
from flask import Flask, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import logging
import subprocess
import time
import tempfile

UPLOAD_FOLDER = os.path.join(os.environ['HOME'],'flask_uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'ppt', 'xls', 'doc'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#######################################

import base64
import atexit
from PIL import Image
from thumbnailer import library as thumb


os.environ['UNO_CONNECTION'] = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
'''
Remember to run the following:
  soffice --accept="socket,host=localhost,port=2002;urp;" --headless --invisible --nocrashreport --nodefault --nofirststartwizard --nologo --norestore
'''
def get_thumbnail(src_path, size):
    return thumb.get(file(src_path), width=size[0], height=size[1])    

#######################################

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    # POST request
    if request.method == 'POST':

        logging.warn(request.headers)
        logging.warn(request.files)
        
        if request.files.get('file', None) is None:
            msg = "Bad request: 'files' was found in request"            
            resp = make_response(msg, 400)
            return resp

        ufile = request.files.get('file', None)
        
        if ufile and allowed_file(ufile.filename):
            filename = secure_filename(ufile.filename)
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            ufile.save(dest_path)

            ### Generate Thumbnail ###
            errors = {}

            if request.form.get('thumbnail',"no").lower() == "yes":
                size_str = request.form.get('thumbnail_size',"300x300")
                size = map(int, size_str.split("x"))
                try:
                    thumb_file = get_thumbnail(dest_path, size)
                except Exception as e:
                    errors['thumbnail'] = str(e)

            if request.form.get('save_orig',"no") == "no":
                os.unlink(dest_path)

            msg = {}
            if len(errors):
                code = 501
                msg['errors'] = errors
                resp = make_response(jsonify(msg), code)
                resp.headers['Content-type'] = "application/json"
                return resp
            else:
                response = make_response(thumb_file.read())
                response.headers['Content-Type'] = 'image/png'
                response.headers['Content-Disposition'] = "attachment; filename=thumbnail.png"
                return response

        else:
            msg = "Invalid file, supported types: %s" % ','.join(list(ALLOWED_EXTENSIONS))
            resp = make_response(msg, 400)
            return resp

    # GET request
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
         <input type=hidden name="thumbnail" value="yes">
         <input type=hidden name="thumbnail_size" value="500x500"
    </form>
    '''

#######################################


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
