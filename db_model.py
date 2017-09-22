#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Author: Danny
# @Date: 2017-09-22 21:46:20
# @Last Modified by:   Danny
# @Last Modified time: 2017-09-22 21:46:20

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.apps import custom_app_context as pwd_context

engine = create_engine(
    "mysql+pymysql://root:Codanyap8121@127.0.0.1/users?charset=utf8",
    max_overflow=10,
    encoding='utf-8')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    """docstring for User"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(128))
    token = Column(String(256))
    end_time = Column(String(256))

    def __repr__(self):

        output = "('%s','%s','%s','%s','%s')" % (self.id, self.username,
                                                 self.password_hash,
                                                 self.token, self.end_time)
        return output

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    text = Column(String(1000))
    creat_time = Column(String(20))

    def __repr__(self):
        output = "{'id':'%s','title':'%s','text':'%s','creat_time':'%s'}" % (
            self.id, self.title, self.text, self.creat_time)
        return output

    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'title': self.title,
    #         'text' : self.text,
    #         'create_time' : self.creat_time
    #     }


def hash_password(password):
    return pwd_context.encrypt(password)
