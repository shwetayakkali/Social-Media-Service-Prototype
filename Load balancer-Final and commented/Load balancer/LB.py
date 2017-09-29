
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
import os
import requests, ast
# This is the Load Balancer.
# It receives requests from users. By running round robin it selects the container to serve the request.
# Forwards the request to selected container and waits for reply.as
# On receiving results it create web page and send it to user's browser.
#
# @ authors	Shweta Yakkali, Niraj Dedhia

# Global variables
app = Flask(__name__)
COUNTER = -1; # Round robin counter
container = ['http://yes.cs.rit.edu:8001','http://yes.cs.rit.edu:8002','http://yes.cs.rit.edu:8003'] # Total number of connected containers
#container = ['http://yes.cs.rit.edu:8001','http://yes.cs.rit.edu:8003']

app.config['UPLOAD_FOLDER'] = './images' # Location to store images
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# allowed_file() : It checks the attached file format.
# Validate the format of file.
#
# @param : filename
#
# @return : None
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# home() : This method is called when user try to access service.
# It will display the login page.
#
# @param : None
#
# @return : Login.html
@app.route('/')
def home():
    if not session.get('uid'):
        return render_template('login.html')

# do_admin_login() : This method is called when user want to login. It displays the login.html
# If user is already logged in then it will display the profile page of respective user.
# It sets the session variables and store uid for maintaining session.
#
# @param : None
#
# @return : Login.html or Profile.html
@app.route('/login', methods=['POST'])
def do_admin_login():

    username = str(request.form['username'])
    password = str(request.form['password'])

    d = fetchJsonfromAPI("/login/"+username+"/"+password);
    d = d.json()

    if d!="NO":
        session['uid'] = d['id']
        return render_template('profile.html',d = d)
    else:
        flash('wrong password!')
    return home()

# register() : This method is called when first time user wants to register.
# It will display the register page and this register.html performs the validation.
#
# @param : None
#
# @return : register.html
@app.route('/register', methods=['GET','POST'])
def register():

    if (request.method == "POST"):
        #print("Hello")
        username = str(request.form['username'])
        password = str(request.form['password'])
        email = str(request.form['email'])
        name = str(request.form['name'])
        status = str(request.form['status'])
        file = request.files['image']
        msg = "abc.jpg"
        if file and allowed_file(file.filename):
            filename=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg = str(filename);

        d = fetchJsonfromAPI("/register/"+username+"/"+password+"/"+email+"/"+name+"/"+status+"/"+msg);
        d = d.json()

        session['uid'] = d['id']
        return render_template('profile.html',d = d)

    else:
        return render_template('register.html')

# logout() : This method is called when user clicks logged out button.
# It clears the session coockie.
#
# @param : None
#
# @return : login.html
@app.route("/logout")
def logout():
    global COUNTER;

    session['uid'] = 0
    return redirect("/")

# friend() : This method is called when user wants to see the friends list.
# Display friend.html which has list of friends of the particular user.
# Here user can send messages and images to his friends.
#
# @param : username
#
# @return : friend.html
@app.route("/friend/<uname>",methods=["POST"])
def friend(uname):

    #print(str(session.get('uid')))
    d = fetchJsonfromAPI("/friend/"+str(session.get('uid'))+"/"+str(uname));
    d = d.json()
    return render_template('friends.html',d = d, uname = str(uname))

# sendMessage() : This post method gets called when user intend to send message.
# This method make api call to the internal flask application which is running on the server container.
#
# @param : friendid, friendname, username
#
# @return : profile.html
@app.route("/sendMessage/<fid>/<fname>/<uname>",methods=['POST'])
def sendMessage(fid,fname,uname):

    msg = str(request.form['msg'])
    d = fetchJsonfromAPI("/sendMessage/"+str(fid)+"/"+str(fname)+"/"+str(session.get('uid'))+"/"+str(uname)+"/"+str(msg));
    d = d.json()

    return render_template('profile.html',d = d)

# sendImage() : This post method gets called when user intend to send an image.
# This method make api call to the internal flask application which is running on the server container.
#
# @param : friendid, friendname, username
#
# @return : profile.html
@app.route("/sendImage/<fid>/<fname>/<uname>",methods=['POST'])
def sendImage(fid,fname,uname):

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename=file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        msg = str(filename);

    d = fetchJsonfromAPI("/sendImage/"+str(fid)+"/"+str(fname)+"/"+str(session.get('uid'))+"/"+str(uname)+"/"+str(msg));
    d = d.json()

    return render_template('profile.html',d = d)

# inbox() : This method display the inbox.html of user.
# This page contains the information of received images and messages from friends.
# Method make api call to internal flask application on one of the server container to fetch the results.
#
# @param : username
#
# @return : inbox.html
@app.route("/inbox/<uname>",methods=['POST'])
def inbox(uname):

    d = fetchJsonfromAPI("/inbox/"+str(session.get('uid'))+"/"+str(uname));
    d = d.json()
    print(d["0"])
    return render_template('inbox.html',rt=d["0"] ,ri=d["1"])

# uploads() : To upload the display pic for the new user.
#
# @param : filename
#
# @return : None
@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(app.config['UPLOAD_FOLDER'], str(filename))

# fetchJsonfromAPI() : Round robin method...this method select the container based on the
# round robin container. It forwards the requests to server container and fetch the
# results in JSON String.
#
# @param : API string
#
# @return : Json string
def fetchJsonfromAPI(string):
    global COUNTER;

    COUNTER+= 1;
    server = container[int(COUNTER)%int(len(container))];
    a = requests.post(str(server)+str(string))
    return (a)

# This is to initialtes the load balancer for the first time.
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)