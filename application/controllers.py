import os
import datetime
from flask import Flask,request,redirect,url_for,render_template
from flask import current_app as app
from application.models import User,TrackerType,Tracker,LogTracker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import date


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo = True)
Session = sessionmaker(bind = engine)
session = Session()

current_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.dirname(current_dir)+"\db_directory"
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(db_dir,"testdb.sqlite3")
db=SQLAlchemy()

@app.route("/", methods=["GET"])    
def login():  
    return render_template("login.html")
    
@app.route("/addTracker/<string:userName>", methods=["GET"])    
def addTracker(userName):  
     result = session.query(TrackerType).all()
     trackertypes = []
     for row in result:
        print(row.trackertypeid,row.trackertype)
        trackerType = TrackerType(trackertypeid=row.trackertypeid,trackertype=row.trackertype)
        trackertypes.append(trackerType)
     session.close()
     return render_template("addTracker.html",trackertypes=trackertypes,username=userName)

@app.route("/addTracker/<string:userName>", methods=["POST"])    
def addedTracker(userName):  
     trackerName = request.form['trackerName']
     trackerDesc = request.form['trackerDesc']
     typevalue = request.form['typevalue']
     typeidws = typevalue.split('-')
     typeid = typeidws[0].strip()
     settings = request.form['settings']
     result = User.query.filter_by(username=userName) 
     userIdForTracker = ''
     for row in result:
        print(row.user_id)
        userIdForTracker  = row.user_id
     tracker  = Tracker(trackerName = trackerName,trackerDesc= trackerDesc ,trackerType =typeid , settings = settings, userid = userIdForTracker)
     try:
        session.add(tracker)
        session.commit()
     except:
        session.rollback()
        return render_template("userNotification.html",userMessage="There was an error adding the Tracker")
     finally:
        session.close()
     return redirect(url_for('landingPage',username=userName))

@app.route("/landingPage/<string:username>", methods=["GET"])    
def landingPage(username):
     userResult = User.query.filter_by(username=username) 
     userIdForTracker = ''
     loggerResult = []
     trackerIdForTracker = ''
     for row in userResult:
        print(row.user_id)
        userIdForTracker  = row.user_id
     trackerResult = Tracker.query.filter_by(userid=userIdForTracker)
     trackersforDisplay =[]
     lastTracked={}
     for row in trackerResult:
        tracker = Tracker(trackerid = row.trackerid,trackerName = row.trackerName, trackerType = row.trackerType,settings = row.settings, userid = row.userid)
        trackerIdForTracker=row.trackerid
        logTracker = LogTracker.query.filter_by(userid=userIdForTracker,trackerid =trackerIdForTracker ).order_by(LogTracker.logdate.desc()).first()
        print(logTracker.logdate)
        print(logTracker.trackerid)
        #2022-03-22
        logTracker.logdate
        dbdate = datetime.datetime.strptime(logTracker.logdate, "%Y-%m-%d").strftime("%Y-%m-%d")
        print("dbdate",dbdate)
        currentDate = datetime.date.today().strftime("%Y-%m-%d")
        print("currentDate",currentDate)
        delta = datetime.datetime.strptime(currentDate,"%Y-%m-%d")-datetime.datetime.strptime(dbdate,"%Y-%m-%d")
        print("delta is :",delta.days)
        lastTracked[trackerIdForTracker]=delta.days
        trackersforDisplay.append(tracker)
       
  
     return render_template("landingPage.html",username=username,trackers=trackersforDisplay,lastTracked=lastTracked)
    
@app.route("/logTracker/<int:userId>/<int:trackerId>", methods=["GET"])    
def logTracker(userId,trackerId):  
    print(userId,trackerId)
    username=''
    trackername=''
    trackertype=''
    settings=''
    userresult = User.query.filter_by(user_id=userId)
    for row in userresult:
        username=row.username
    trackerresult = Tracker.query.filter_by(trackerid=trackerId)
    for row in trackerresult:
        trackername=row.trackerName
        trackertype=row.trackerType
        settings=row.settings
    
    return render_template("logTracker.html",username=username,trackername=trackername,userid=userId,trackerid=trackerId,trackertype=trackertype,settings=settings)
    
@app.route("/trendLines/<int:userId>/<int:trackerId>", methods=["GET"])    
def trendLines(userId,trackerId):  
    print(userId,trackerId)
    username=''
    trackername=''
    trackertype=''
    settings=''
    userresult = User.query.filter_by(user_id=userId)
    for row in userresult:
        username=row.username
    trackerresult = Tracker.query.filter_by(trackerid=trackerId)
    for row in trackerresult:
        trackername=row.trackerName
        trackertype=row.trackerType
        settings=row.settings
    
    return render_template("trendLines.html")
    
@app.route("/logTracker/<int:userId>/<int:trackerId>", methods=["POST"])    
def loggedTracker(userId,trackerId):  
    print(request.form['username'])
    print(request.form['trackername'])
    print(request.form['userid'])
    print(request.form['trackerid'])
    print(request.form['trackertype'])
    logDate = request.form['date']
    logTime = request.form['time']
    if request.form['trackertype'] == '2':
        value = request.form.get('exampleRadios')
    elif request.form['trackertype'] == '1':
        value = request.form['trackedvalue']
    elif request.form['trackertype'] == '3':
        value = request.form['trackedvalue']
    print(value)
    notes=request.form['notes']
    
    logTracker = LogTracker(userid=userId,trackerid=trackerId,logdate=logDate,logtime=logTime,value=value,notes=notes)
    try:
        session.add(logTracker)
        session.commit()
    except:
        session.rollback()
        return render_template("userNotification.html",userMessage="Error during adding log activity. Please try later")
    finally:
        session.close()
    
    return redirect(url_for('landingPage',username=request.form['username']))
    
@app.route("/", methods=["POST"])    
def launch():  
    if request.form['submit_button'] == 'Login':
        username = valid_login(request.form['userName'],request.form['password'])
        print(username)
        if(username == 'notFound'):
            return render_template("userNotification.html",userMessage="Email-iD/Password combination incorrect. Please login using valid credentials")
        else:
            return redirect(url_for('landingPage',username=username))
    else:
        if request.form['submit_button'] == 'createUser':
           return redirect(url_for('createUser'))
        
        
    return render_template("login.html")

@app.route("/createUser",methods=["GET"])
def createUser():
  #  print(db_dir)
  #  result = db.session.execute("select * from user")
  #  print(current_dir)
  #  for row in result:
  #      print(row)
    return render_template("createUser.html")
    
@app.route("/createUser",methods=["POST"])
def userCreated():
    username=(request.form['userName'])
    userEmail=(request.form['userEmail'])
    userPassword=(request.form['userPassword'])
    user  = User(username = username,email= userEmail , password = userPassword)
    try:
        session.add(user)
        session.commit()
    except:
        session.rollback()
        return render_template("userNotification.html",userMessage="Email Id Already Registered. Please login using the registered credentials")
    finally:
        session.close()
    return render_template("userCreateConfirm.html",username=username)

def valid_login(userEmail,userPassword):
        result = User.query.filter_by(email=userEmail,password=userPassword)
        for row in result:
            return row.username
        return 'notFound'
    