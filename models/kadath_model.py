import inspect
import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.dialects.mysql import MEDIUMTEXT, TIMESTAMP, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from config import conn_string

Base = declarative_base()


class KadathNote(Base):

    def __init__(self, values):
        self.id = values.get('id')
        self.user_id = values.get('user_id')
        self.title = values.get('title')
        self.text = values.get('text')
        self.created = values.get('created')
        self.modified = values.get('modified')

    def __str__(self):
        return '[{self.id}] Author: {self.user_id}, Title: {self.title}'.format(self=self)

    def to_dict(self):
        note_dict = {}
        note_dict['id'] = self.id
        note_dict['user_id'] = self.user_id
        note_dict['title'] = self.title
        note_dict['text'] = self.text
        note_dict['created'] = str(self.created)
        note_dict['modified'] = str(self.modified)
        return note_dict

     #====== Table options ======#

    __tablename__ = 'notes'

    id = Column(Integer(), primary_key=True, nullable=False)
    user_id = Column(Integer(), ForeignKey('users.id'))
    title = Column(String(300))
    text = Column(MEDIUMTEXT())
    created = Column(DATETIME())
    modified = Column(DATETIME())


class User(Base):

    def __init__(self, values):
        self.id = values.get('id')
        self.email = values.get('email')
        self.password = values.get('password')
        self.firstname = values.get('firstname')
        self.lastname = values.get('lastname')

    def __str__(self):
        return '{self.firstname} {self.lastname} <{self.email}>'.format(self=self)

    def to_dict(self):
        user_dict = {}
        user_dict['id'] = self.id
        user_dict['email'] = self.email
        user_dict['password'] = self.password
        user_dict['firstname'] = self.firstname
        user_dict['lastname'] = self.lastname
        return user_dict

    # ====== Table options ====== #

    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True, nullable=False)
    authentications = relationship('Authentication')
    notes = relationship('KadathNote')
    email = Column(String(100))
    password = Column(String(100))
    firstname = Column(String(100))
    lastname = Column(String(100))


class Authentication(Base):

    def __init__(self, values):
        self.id = values.get('id')
        user_id = values.get('user_id')
        self.auth_key = values.get('auth_key')


    def __str__(self):
        return '{self.id}: User ID: {self.user_id}, Auth key: <{self.auth_key}>'.format(self=self)

    def to_dict(self):
        note_dict = {}
        note_dict['id'] = self.id
        note_dict['user_id'] = self.user_id
        note_dict['auth_key'] = self.auth_key
        return note_dict

    # ====== Table options ====== #

    __tablename__ = 'authentications'

    id = Column(Integer(), primary_key=True, nullable=False)
    user_id = Column(Integer(), ForeignKey('users.id'))
    auth_key = Column(String(100))


engine = create_engine(conn_string)
Base.metadata.create_all(engine)
