import os
from flask import Flask, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename

import subprocess

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
  soffice --accept="socket,host=localhost,port=2002;urp; --headless --invisible --nocrashreport --nodefault --nofirststartwizard --nologo --norestore
'''
def get_thumbnail(src_path, size):
    t = thumb.get(file(src_path), width=size[0], height=size[1])
    i = Image.open(t)
    w, h = i.size
    w,h = size

    t.seek(0)
    tdata = {
        "data": base64.b64encode(t.read()),
        "width": w,
        "height": h,
    }
    return tdata

#######################################

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    # POST request
    if request.method == 'POST':
        ufile = request.files['file']
        if ufile and allowed_file(ufile.filename):
            filename = secure_filename(ufile.filename)
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            ufile.save(dest_path)

            ### Generate Thumbnail ###
            errors = {}

            if request.form['thumbnail'].lower() == "yes":
                size_str = request.form.get('thumbnail_size',"300x300")
                size = map(int, size_str.split("x"))
                try:
                    tdata = get_thumbnail(dest_path, size)
                except Exception as e:
                    errors['thumbnail'] = str(e)
                    tdata = None
            else:
                tdata = None

            msg = {
                "filename": filename,
                "thumbnail": tdata
            }
            if len(errors):
                code = 501
                msg['errors'] = errors
            else:
                code = 200

            resp = make_response(jsonify(msg), code)
            resp.headers['Content-type'] = "application/json"
            return resp

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
    </form>
    '''

#######################################


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
