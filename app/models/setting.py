from app import db


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255))
    value = db.Column(db.String(255))

    @staticmethod
    def get(key):
        return Setting.query.filter_by(key=key).first()

    @staticmethod
    def set(key, value):
        setting = Setting.query.filter_by(key=key).first()
        if setting is None:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
            db.session.commit()
        setting.value = value
        db.session.commit()
