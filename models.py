# backend/models.py
from datetime import datetime
from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class PasswordHistory(db.Model):
    __tablename__ = 'password_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    length = db.Column(db.Integer, nullable=False)
    include_numbers = db.Column(db.Boolean, nullable=False)
    include_specials = db.Column(db.Boolean, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    passwords = db.Column(db.Text, nullable=False)
