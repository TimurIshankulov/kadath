import inspect
import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.dialects.mysql import MEDIUMTEXT, TIMESTAMP
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
        self.title = values.get('title')
        self.text = values.get('text')
        self.created = values.get('created')
        self.modified = values.get('modified')

    def __str__(self):
        return '[{self.id}] Title: {self.title}'.format(self=self)

    
    def to_dict(self):
        note_dict = {}
        note_dict['id'] = self.id
        note_dict['title'] = self.title
        note_dict['text'] = self.text
        note_dict['created'] = self.created
        note_dict['modified'] = self.modified

     #====== Table options ======#

    __tablename__ = 'notes'

    id = Column(Integer(), primary_key=True, nullable=False)
    title = Column(String(300))
    text = Column(MEDIUMTEXT())
    created = Column(TIMESTAMP())
    modified = Column(TIMESTAMP())


engine = create_engine(conn_string)
Base.metadata.create_all(engine)
