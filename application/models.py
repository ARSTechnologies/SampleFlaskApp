from .database import db

class User(db.Model):
    __tablename__='user'
    user_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    
class Tracker(db.Model):
    __tablename__='tracker'
    trackerid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    trackerName = db.Column(db.String)
    trackerDesc = db.Column(db.String)
    trackerType = db.Column(db.Integer)
    settings = db.Column(db.String)
    userid = db.Column(db.Integer)
    
class TrackerType(db.Model):
    __tablename__='trackertype'
    trackertypeid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    trackertype = db.Column(db.String)
    
class LogTracker(db.Model):
    __tablename__='trackerlog'
    logid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    userid = db.Column(db.Integer)    
    trackerid = db.Column(db.Integer)
    logdate = db.Column(db.String)
    logtime = db.Column(db.String)
    value = db.Column(db.String)
    notes = db.Column(db.String)
   
    
