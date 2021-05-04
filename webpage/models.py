from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))


class RawData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_name = db.Column(db.String(150), unique=True)
    start_frame = db.Column(db.Integer)
    end_frame = db.Column(db.Integer)


class LangData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rawdata_id = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer)
    lang_ann = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=func.now())