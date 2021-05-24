import json
import os

from  mongoengine import connection
from mongoengine.queryset import QuerySet
import click

from language import load_sentences
from models import LanguageText
from connection import init_db, get_db



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
@click.option('-d', '--database', default=os.environ.get('LANGUAGE_URI', 'mongodb://localhost:27017/language'))
@click.pass_context
def populate(ctx, database):
    init_db(database)
    db = get_db()
    sentences = load_sentences()
    for key, value in sentences.items():
        collection = db[key]
        values = []
        for k, v in value.items():
            values = get_value(k, v, key)

if __name__ == '__main__':
    cli()
