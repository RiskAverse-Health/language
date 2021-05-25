import json
import os
import codecs
from  mongoengine import connection
from mongoengine.queryset import QuerySet
import click

import language

from models import LanguageText
from connection import init_db, get_db

BASE_FOLDER = os.path.dirname(os.path.realpath(__file__))
LANGUAGE_FOLDER = os.path.join(BASE_FOLDER, 'static', 'language')

def load_sentences():
    """
    Gets all language config
    """
    _sentences = {}
    for subdir, dirs, files in os.walk(LANGUAGE_FOLDER):
        for _file in files:
            with codecs.open(os.path.join(subdir, _file), 'r', 'utf-8') as lang_file:
                _sentences.update(json.load(lang_file))
    return _sentences

sentences = load_sentences()

def get_value(key, value, collection):
    print(key)
    if isinstance(value, dict) and 'en' in value:
        lt = LanguageText.switch_collection(LanguageText(id=key, **value), collection)
        lt.save()
    else:
        for k, v in value.items():
            print(v)
            get_value(f'{key}.{k}', v, collection)



@click.group()
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.option('-d', '--database', default=os.environ.get('LANGUAGE_URI', language.DEFAULT_LANGUAGE_HOST))
@click.pass_context
def populate(ctx, database):
    language.initialize(database)
    db = get_db()
    sentences = load_sentences()
    for key, value in sentences.items():
        collection = db[key]
        values = []
        for k, v in value.items():
            values = get_value(k, v, key)

if __name__ == '__main__':
    cli()
