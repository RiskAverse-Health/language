import os
from mongoengine import connect, connection


def init_db(db_string):
    connect(host=db_string)
    db = connection.get_db()

def get_db():
    return connection.get_db()
