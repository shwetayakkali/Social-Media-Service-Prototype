
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
import  simplejson
# This code serves the requests coming from load balancer.
# Each containers will run this code and they will get selected by load balancer.
# This containers are connected with all the distributed database.
# Based on the username hashed values it selects the database.
#
# @ authors	Shweta Yakkali, Niraj Dedhia

# Global variables
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@mysql/socialnetwork';
db = SQLAlchemy(app)
dbString = ['mysql+pymysql://root:root@mysql/socialnetwork','mysql+pymysql://root:root@mysql2/socialnetwork'] # Distributed DBs

# getUser() : It returns the user information
#
# @param : uid
#
# @return : user information
@app.route('/getUser/<uid>', methods=['POST'])
def getUser(uid):
    return "USER INFORMATION"

# login() : It will get called when load balancer sends the login request.
# Database gets selected based on hash value of username.
# Fetch the results from db and convert it in to JSON string.
# Returns the results to load balancer
#
# @param : username, password
#
# @return : user profile
@app.route('/login/<uname>/<upwd>', methods=['POST'])
def login(uname,upwd):
    global db;

    dbSelection(hash(uname))
    sql = text("select id,name,username,status,dp from user where username = '"+uname+"' and password = '"+upwd+"'")
    result = db.engine.execute(sql)

    a = 0;
    d={};
    for row in result:
        a = row[0];

    if a!=0:
        d['id']=str(row[0])
        d['name'] = str(row[1])
        d['username'] = str(row[2])
        d['status'] = str(row[3])
        d['dp'] = str(row[4])
        row = simplejson.dumps(d)
        return (row)
    else:
        return (d)

# login() : It will get called when load balancer sends the registeration request.
# Database gets selected based on hash value of username.
# Stores the value in respected db and user table.
# Fetch the results from db and convert it in to JSON string.
# Returns the results to load balancer
#
# @param : username, password, email, name, status, dp which is image location string
#
# @return : user profile
@app.route('/register/<uname>/<upwd>/<email>/<name>/<status>/<dp>', methods=['POST'])
def register(uname,upwd,email,name,status,dp):

    dbSelection(hash(uname))

    sql = text("INSERT INTO user(username, password, email, Name, status, dp) VALUES ('"+str(uname)+"','"+str(upwd)+"','"+str(email)+"','"+str(name)+"','"+str(status)+"','"+str(dp)+"')")
    result = db.engine.execute(sql)

    sql = text("select id,name,username,status,dp from user where username = '"+uname+"' and password = '"+upwd+"'")
    result = db.engine.execute(sql)
    d={};
    for row in result:
        a = row[0]

    d['id']=str(row[0])
    d['name'] = str(row[1])
    d['username'] = str(row[2])
    d['status'] = str(row[3])
    d['dp'] = str(row[4])
    row = simplejson.dumps(d)
    return (row)

# friend() : It will get called when load balancer asks for friend list.
# Database gets selected based on hash value of username.
# Fetch the results from friends table and convert it in to JSON string.
# Returns the results to load balancer
#
# @param : uid, username
#
# @return : list of friends in JSON string
@app.route("/friend/<uid>/<uname>", methods=['POST'])
def friend(uid,uname):


    dbSelection(hash(uname))
    sql = text("select fid, fname from friends where uid = "+str(uid)+"")
    r1 = db.engine.execute(sql)

    outer = {}
    ctr = 1;

    for row in r1:
        inner={}
        inner['fid']=str(row[0])
        inner['fname']=str(row[1])

        dbSelection(hash(inner['fname']))
        sql=text("select status, dp from user where id = "+inner['fid']+"")
        r2 = db.engine.execute(sql)
        for row1 in r2:
            inner['status']=str(row1[0])
            inner['dp']=str(row1[1])

        outer[ctr]=inner
        ctr+=1
    row = simplejson.dumps(outer)
    return (row)

# sendMessage() : It will get called when user wants to sends message to his friend.
# Select databse based on username hash value.
# stores the informations in recvtable of user and send table of friend.
# Friend may be listed in same db or different so it takes care of that by
# moving between dbs.
#
# @param : friend id, friend name, uid, username, message
#
# @return : user profile
@app.route("/sendMessage/<fid>/<fname>/<uid>/<uname>/<msg>",methods=['POST'])
def sendMessage(fid,fname,uid,uname,msg):
    # Hash of fid andnselect db and add entry to receivemsgimg table
    dbSelection(hash(fname))
    sql = text("insert into recmsgimg values ("+fid+","+uid+",'"+uname+"',0,1,'"+str(msg)+"')")
    r = db.engine.execute(sql)

    # Hash of uid and select db and add entry to sendmsgimg table
    dbSelection(hash(uname))
    sql = text("insert into sendmsgimg values ("+uid+","+fid+",0,1,'"+str(msg)+"')")
    r = db.engine.execute(sql)

    sql = text("select id,name,username,status,dp from user where id = '"+uid+"'")
    result = db.engine.execute(sql)
    d={};
    for row in result:
        a = row[0]

    d['id']=str(row[0])
    d['name'] = str(row[1])
    d['username'] = str(row[2])
    d['status'] = str(row[3])
    d['dp'] = str(row[4])
    row = simplejson.dumps(d)

    return (row)

# sendImage() : It will get called when user wants to sends image to his friend.
# Select database based on username hash value.
# stores the information in recvtable of user and send table of friend.
# Friend may be listed in same db or different so it takes care of that by
# moving between dbs.
#
# @param : friend id, friend name, uid, username, image location string
#
# @return : user profile
@app.route("/sendImage/<fid>/<fname>/<uid>/<uname>/<filename>",methods=['POST'])
def sendImage(fid,fname,uid,uname,filename):

    # Hash of fid andnselect db and add entry to receivemsgimg table
    dbSelection(hash(fname))
    sql = text("insert into recmsgimg values ("+fid+","+uid+",'"+uname+"',1,0,'"+str(filename)+"')")
    r = db.engine.execute(sql)

    # Hash of uid and select db and add entry to sendmsgimg table
    dbSelection(hash(uname))
    sql = text("insert into sendmsgimg values ("+uid+","+fid+",1,0,'"+str(filename)+"')")
    r = db.engine.execute(sql)


    sql = text("select id,name,username,status,dp from user where id = '"+uid+"'")
    result = db.engine.execute(sql)
    d={};
    for row in result:
        a = row[0]

    d['id']=str(row[0])
    d['name'] = str(row[1])
    d['username'] = str(row[2])
    d['status'] = str(row[3])
    d['dp'] = str(row[4])
    row = simplejson.dumps(d)

    return (row)

# inbox() : It will get called when user wants to see received messages and images.
# Select database based on username hash value.
# Fetch the results from receive table.
# Returns the results to load balancer in JSON string format.
#
# @param : uid, username
#
# @return : received messages and images
@app.route("/inbox/<uid>/<uname>", methods=['POST'])
def inbox(uid,uname):
    dbSelection(hash(uname))
    sql = text("select fid, fname, string from recmsgimg where uid = "+uid+" and text = 1")
    r = db.engine.execute(sql)
    d={};
    ctrt=0;
    rt = {};
    ctrr=0;
    ri ={};
    row = []
    a = 0;
    for row in r:
        a = row[0]
        d={}
        if(a>0):
          d['fid']=str(row[0])
          d['fname'] = str(row[1])
          d['string'] = str(row[2])
        rt[ctrt] = d
        ctrt+=1
    
    print('hereeeeee',str(uid))
    sql = text("select fid, fname, string from recmsgimg where uid = "+uid+" and img = 1")
    r = db.engine.execute(sql)
    d={};
    for row in r:
        a = row[0]
        d = {}
        if(a>0):
            d['fid']=str(row[0])
            d['fname'] = str(row[1])
            d['string'] = str(row[2])
        ri[ctrr] = d
        ctrr+=1

    row = {};
    row[0]=rt;
    row[1]=ri;
    print(row)
    row=simplejson.dumps(row)
    return row

# hash() : It calculates the hash value of username.
# This method helps container to decide which databse to select for which user.
#
# @param : username
#
# @return : hash value of username
def hash(uname):
    global dbString;

    a = 0;
    for c in str(uname):
        a = a + (ord)(c);
    return a%len(dbString);

# dbSelection() : Method selects the DB based on hash value.
#
# @param : hash(sername)
#
# @return : None
def dbSelection(hashId):
    global db;
    global dbString;

    app.config['SQLALCHEMY_DATABASE_URI']=dbString[hashId];


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)