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

def convert_text_to_key(text):
    text = text.lower()

    text = text.replace('+', ' plus').replace('-', ' ')
    toks = text.split()
    num_text = ''
    for tok in toks:
        if tok.isnumeric():
            num_text += tok

    remove = [',', '$', ' ', '.']
    for r in remove:
        text = text.replace(r, '')

    max_size = 7
    if len(text) <= max_size:
        return text

    return (num_text + text[::max(2, int(len(text)/max_size))])[:max_size]

@click.group()
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.option('-d', '--database', default=os.environ.get('LANGUAGE_URI'))
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

@cli.command()
@click.option('-d', '--database', default=os.environ.get('LANGUAGE_URI'))
@click.option('-f', '--file')
@click.pass_context
def questions(ctx, database, file):
    language.initialize(database)

    ids = []
    data = {}
    with codecs.open(file, 'r', 'utf-8') as question_file:
        data.update(json.load(question_file))

    new_data = {}
    answer_to_id = {}
    id_to_answer_text = {}
    categories = {}
    for key, val in data.items():
        if isinstance(val, dict):
            new_val = val.copy()
            # Convert question text
            if question := val.get('question'):
                lt = LanguageText.switch_collection(LanguageText(id=f'questions.{key}', **question), 'questions')
                new_val['question'] = f'questions.questions.{key}'
                lt.save()
            
            if category := val.get('category'):
                cid = 'categories.' + '_'.join(category['en'].lower().replace('&', '').replace(',', '').replace('/', '_').split())
                categories[cid] = category
                new_val['category'] = f'questions.{cid}'
                #lt = LanguageText.switch_collection(LanguageText(id=f'categories.{key}', **category), 'questions')
                lt.save()

            if title := val.get('title'):
                lt = LanguageText.switch_collection(LanguageText(id=f'titles.{key}', **title), 'questions')
                new_val['title'] = f'questions.titles.{key}'
                lt.save()

            if short_title := val.get('shortTitle'):
                new_val['shortTitle'] = f'questions.short_titles.{key}'
                lt = LanguageText.switch_collection(LanguageText(id=f'short_titles.{key}', **short_title), 'questions')
                lt.save()

            if short_title_alt := val.get('shortTitleAlt'):
                new_val['shortTitleAlt'] = f'questions.short_title_alts.{key}'
                lt = LanguageText.switch_collection(LanguageText(id=f'short_title_alts.{key}', **short_title_alt), 'questions')
                lt.save()

            
            if placeholder := val.get('placeholder'):
                idd = None
                lt = None
                if isinstance(placeholder, dict):
                    idd = 'placeholders.enter_address'
                    lt = LanguageText.switch_collection(LanguageText(id=idd, **placeholder), 'questions')
                else:
                    idd = 'placeholders.date'
                    lt = LanguageText.switch_collection(LanguageText(id=idd, en=placeholder, es=placeholder), 'questions')

                lt.save()
                new_val['placeholder'] = f'questions.{idd}'
            

            # Convert answers
            for f in ('answers', 'brackets'):
                if f in val:
                    answers = []
                    for answer in val[f]:
                        if 'text' in answer:
                            new_answer = answer.copy()
                            if isinstance(answer['text'], dict):
                                text = answer['text']['en']
                                answer_id = 'anegtv' if text == 'A negative' else convert_text_to_key(text)

                                if answer_id == 'ittctna':
                                    continue

                                if text not in answer_to_id:
                                    new_answer['text'] = f'questions.answers.{answer_id}'

                                    skip = False
                                    for i in ids:
                                        if answer_id == i[0]:
                                            skip = True
                                            if text.lower() == i[1].lower():
                                                t1c = sum(1 for c in text if c.isupper())
                                                t2c = sum(1 for c in i[1] if c.isupper())

                                                best = text if t1c > t2c else i[1]
                                                worst = i[1] if t1c > t2c else text
                                                answer_to_id[best] = answer_id
                                                if worst in answer_to_id:
                                                    del answer_to_id[worst]

                                                if text == best:
                                                    ids.append((answer_id, best))
                                                break
                                            else:
                                                print(f'duplicate - {answer_id} ({text}) - {i[1]}')

                                    if not skip:
                                        answer_to_id[text] = answer_id
                                        id_to_answer_text[answer_id] = answer['text']
                                        ids.append((answer_id, text))
                                else:
                                    new_answer['text'] = f'questions.answers.{answer_to_id[text]}'

                            else:
                                answer_id = answer['text'].lower().replace('/', '_').replace(' ', '_')

                                to_remove = ['\'', '(', ')', ',', '.']
                                for tr in to_remove:
                                    answer_id = answer_id.replace(tr, '')

                                print(answer_id)
                                id_to_answer_text[answer_id] = {
                                    'en': answer['text'],
                                    'es': answer['text']
                                }
                                new_answer['text'] = f'questions.answers.{answer_id}'
                            answers.append(new_answer)
                        else:
                            answers.append(answer)

                    new_val[f] = answers

            new_data[key] = new_val
        else:
            new_data[key] = val

    for aid, texts in id_to_answer_text.items():
        lt = LanguageText.switch_collection(LanguageText(id=f'answers.{aid}', **texts), 'questions')
        lt.save()

    for cid, texts in categories.items():
        lt = LanguageText.switch_collection(LanguageText(id=f'{cid}', **texts), 'questions')
        lt.save()

    with codecs.open('newmasterquestions.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(new_data, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    cli()
