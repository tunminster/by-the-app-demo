from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CallInfo(db.Model):
    __tablename__ = 'CallInfo'
    id = db.Column(db.Integer, primary_key=True)
    call_time = db.Column(db.DateTime, default=datetime.utcnow)
    full_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.DateTime)
    last_four_cc_digits = db.Column(db.String(4))
    contact_number = db.Column(db.String(20))
    action_to_do = db.Column(db.String(100))

    def __repr__(self):
        return f'<CallInfo {self.full_name}>'