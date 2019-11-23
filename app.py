import os
from functools import wraps
from flask import Flask, request, render_template, send_from_directory ,jsonify ,make_response,session
import datetime
import jwt
import pathlib
import json 

app = Flask(__name__)

app.config['SECRET_KEY'] = 'JustDemonstrating'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# @app.route('/unprotected')
# def unprotected():
#     return ''

# @app.route('/protected')
# def protected():
#     return ''

# @app.route('/login')
# def login():
#     auth = request.authorization

#     if auth and auth.password == 'password':
#         return ''
#     return ''

def check_for_token(func):
    @wraps(func)
    def wrapped(*args ,**kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message' : 'Missing token'}) ,403
        try:
            data = jwt.decode(token ,app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Invalid token'}) ,403
        return func(*args ,**kwargs)
    return wrapped

@app.route("/")
def index():
    session['logged_in'] = False
    print(session.get('logged_in'))
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("upload.html")

@app.route('/auth')
@check_for_token
def authorised():
    return render_template("upload.html")

@app.route('/login' ,methods = ['POST'])
def login():
    if request.form['username'] and request.form['password'] == 'password':
        session['logged_in'] = True
        
        a = {
            'user' : request.form['username'],
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds = 60),
            'call' : 0
        }
        token = jwt.encode(a ,app.config['SECRET_KEY'])
        # print(a["call"])
        return jsonify({'token' : token.decode('utf-8')})

    else:
        return make_response('Unable to verify' ,403)



@app.route("/upload", methods=["POST"])
def upload():
    
    target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]
        if (ext == ".jpg") or (ext == ".png"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete.html", image_name=filename)

@app.route('/static/<filename>')
def send_image(filename):
    print('#####filename :',filename)
    return send_from_directory("images", filename)

@app.route('/gallery')
def get_gallery():
    image_names = os.listdir('./images')
    print(image_names)
    return render_template("gallery.html", image_names=image_names)

if __name__ == "__main__":
    app.run(port=4555, debug=True)