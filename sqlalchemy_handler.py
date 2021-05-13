#! /user/bin/env python
# -*- coding:utf-8 -*-
'''built-in'''
import os
import logging
import uuid
import sys
import logging

'''3rd party'''
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Index,
    Binary,
    TIMESTAMP,
    LargeBinary,JSON
)
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import VARCHAR, LONGTEXT

MYSQL_IP = os.environ.get('MYSQL_IP', '172.25.11.23')
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '1qazxsw2')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'ai_service')

Base = declarative_base()


class GroupInfo(Base):
    __tablename__ = 'group_info'    
    group_id    = Column(UUIDType(binary=True), primary_key=True)    
    description = Column(VARCHAR(255))
    # user_number = Column(Integer, nullable=False)


class UserFaceFeature(Base):
    __tablename__ = 'user_face_feature'
    _id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(UUIDType(binary=True), nullable=False)
    face_id         = Column(Integer, nullable=False)
    face_feature    = Column(JSON, nullable=False)
    updated_time    = Column(TIMESTAMP, nullable=False, server_default=text('current_timestamp'))
    bbox            = Column(JSON, nullable=False)
    image_path      = Column(String(512), nullable=False)


class UserInfo(Base):
    __tablename__ = 'user_info'
    _id        = Column(Integer, primary_key=True, autoincrement=True)
    group_id   = Column(UUIDType(binary=True), ForeignKey('group_info.group_id'), nullable=False)
    user_id    = Column(UUIDType(binary=True), nullable=False)
    ts         = Column(TIMESTAMP, nullable=False, server_default=text('current_timestamp'))


class ImageTask(Base):
    __tablename__ = 'image_task'
    _id     = Column(Integer, primary_key=True, autoincrement=True)
    img_id  = Column(UUIDType(binary=True), nullable=False)    
    img     = Column(LONGTEXT, nullable=False)
    # img = Column(LargeBinary(length=(2**32)-1), nullable=False)


class SqlHandler:
    def __init__(self, logger=logging.getLogger(), \
            SQL_USER=MYSQL_USER, SQL_PASS=MYSQL_PASSWORD, \
            SQL_IP=MYSQL_IP, SQL_PORT=MYSQL_PORT, DB_NAME=MYSQL_DATABASE
        ):
        self.logger = logger
        
        endpoint_tmpl = 'mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}'
        self.endpoint = endpoint_tmpl.format(
            username=SQL_USER, password=SQL_PASS, host=SQL_IP, port=SQL_PORT, dbname=DB_NAME)

        self.engine = create_engine(self.endpoint, 
            pool_size=10, 
            pool_timeout=30,
            max_overflow=5
        )
        self.session = sessionmaker(bind=self.engine)()
        self.logger.debug('sql engine and session are created.')

        self.init_db()

    def init_db(self):
        global Base
        Base.metadata.create_all(self.engine)

    def drop_db(self):
        global Base
        Base.metadata.drop_all(self.engine)

    def execute(self, command):
        self.engine.execute(command)

    def get_session(self):
        return self.session
    


