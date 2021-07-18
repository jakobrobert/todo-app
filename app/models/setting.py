from app import db


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255))
    value = db.Column(db.String(255))
