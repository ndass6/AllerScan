from app import db

class Data(db.Model):
    __tablename__ = 'new'
    id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column(db.String)

    def __init__(self, text):
        self.text = text
