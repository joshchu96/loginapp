from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db=SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)


    @classmethod
    def encrpytion(cls,username,password, email, first_name, last_name):
        """hash the password prior to inputting it into the db"""
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        return cls(username=username, password=hashed_pw, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authentication(cls,username,password):
        """check if username is in db && double-check password with hashed password in db"""
        user = User.query.filter_by(username=username).first()
        if(user and bcrypt.check_password_hash(user.password, password)):
            return user
        else:
            return False

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    username =db.Column(db.String(30), db.ForeignKey('users.username'))
    

