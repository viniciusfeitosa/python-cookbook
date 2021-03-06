from datetime import datetime

from . import db  # import ORM instance from __init__.py

from sqlalchemy.dialects import postgresql


# Defining model class with database operations
class NewsModel(db.Model):
    __tablename__ = 'news'  # set table name

    id = db.Column(db.Integer, primary_key=True)  # primary key
    author = db.Column(db.String(150))
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    tags = db.Column(postgresql.ARRAY(db.String))

    # class constructor
    def __init__(self, data):
        self.author = data.get('author')
        self.title = data.get('title')
        self.content = data.get('content')
        self.is_active = data.get('is_active')
        self.tags = data.get('tags')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def list_news():
        return NewsModel.query.all()

    @staticmethod
    def get_news(id):
        return NewsModel.query.get(id)
