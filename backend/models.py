from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    user_name = db.Column(db.String(255))
    user_status = db.Column(db.String(100))
    user_phone = db.Column(db.String(50))
    user_email = db.Column(db.String(255))
    problem_desc = db.Column(db.Text)
    img_path = db.Column(db.String(512))
    status = db.Column(db.Enum('pending','in-progress','completed','pending_sync','online'), default='pending')
    reporter_token = db.Column(db.String(255), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
