from sqlalchemy import *
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, validates, sessionmaker, backref,\
relationship
from hashlib import sha1
import random, string

#import settings
Base = declarative_base()
MIGRATING = True

class User(Base):

    metadata = MetaData()
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    username = Column(String(30), unique = True)
    password = Column(String(40))
    email = Column(String(20))
    credit = Column(Double(precision=None, scale=None, asdecimal=True))
    is_premium = Column(Integer(2))
    salt = Column(String(20))
    last_login = Column(DateTime())
    payments = relationship("Payment", backref="users")

    def __init__(self, *args, **kwargs):
        salt = kwargs.get('salt', False)
        password = kwargs.get('password')
        self.username = kwargs.get('username')
        self.salt = kwargs.get('salt')
        self.password = sha1(password+self.salt).hexdigest() if password else None
        self.email = kwargs.get('email')
        self.is_premium = kwargs.get('is_premium') or 0
        self.last_login = kwargs.get('last_login')

    def migrate(self, engine):
        self.metadata.create_all(engine)

    def validate_password(self, password):
        return (self.password == sha1(password + self.salt).hexdigest())

    @validates('salt')
    def validate_salt(self, key, salt):
        if salt:
            return salt
        else:
           return ''.join(random.sample(string.letters+string.digits, 20))


class Payment(Base):

    metadata = MetaData()
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False,
            unique=False)
    amount = Column(Double(precision=10, scale=2, asdecimal=True))
    status = Column(Integer(2))
    is_suspicious = Column(Integer(2))
    payed_at = Column(DateTime())

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.created_at = kwargs.get('payed_at')

    def migrate(self, engine):
        self.metadata.create_all(engine)

def engine_builder(db='processing_engine'):
    engine = create_engine("mysql://pengine:U1kXVI3Iz@localhost/%s"%db,\
            poolclass=NullPool)
    return engine

def session_builder(engine=None):
    """ builds a session from a database engine and return a
    dictionary with both engine/session pair """

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


TABLES = [Admin, Campaign, InputType, Question, OptionChoice, QuestionOption,
        Answer]

def full_migrate():
    """ recursive migration for all models listed in TABLES list """
    db = session_builder()
    for table in TABLES:
        table_instance = table()
        try:
            table_instance.migrate(db['engine'])
        except Exception as e:
            print e
        db['session'].commit()


