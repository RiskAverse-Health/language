import os
from mongoengine import connect, connection

context = {
    'db': None
}
def ensure_db(db_string):
    if context['db'] is None:
        print("initialize")
        init_db(db_string, False)
    return get_db()

def init_db(db_string, is_default=False):
    alias = 'default' if is_default else 'language'
    print(alias)
    connect(host=db_string, alias=alias)
    context['db'] = True

def get_db():
    return connection.get_db(alias='language')
