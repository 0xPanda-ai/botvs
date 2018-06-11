from app.extensions import db


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, server_default=db.func.now())
    modified_time = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    delete_time = db.Column(db.DateTime, nullable=True)


class TransactionLog(Base):
    __tablename__ = 'transaction_log'
    price = db.Column(db.DECIMAL, nullable=False)
    amount = db.Column(db.DECIMAL, nullable=False)
    type = db.Column(db.INTEGER, nullable=False)


class TextLog(Base):
    __tablename = 'text_log'
    contents = db.Column(db.TEXT, nullable=False)
