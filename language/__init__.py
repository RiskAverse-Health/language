"""
Methods for getting localized text
"""
import os
import json
import codecs

from typing import List, Dict

from .connection import get_db, ensure_db
from .models import LanguageText

DEFAULT_LANGUAGE_HOST =  'mongodb://localhost:27017/language'

context = {}

def initialize(db_uri):
    ensure_db(db_uri)


def set_lang(lang: str):
    context['lang'] = lang

def get_lang():
    return context.get('lang', 'en')


def get_translated_field(field, lang=None):
    """
    Returns localized text for a field. Defaults to 'en' text
    """
    if not isinstance(field, dict):
        return field
    return field.get(lang or get_lang())

def get_texts_from_key_list(keys: List[str], lang: str=None, short: bool=False) -> Dict[str, object]:
    """
    Gets texts based on a list of keys. Returned dict puts text nested in order determined by the key
    """
    texts = {}
    for key in keys:
        text = get_text_from_key(key, lang=lang or get_lang(), short=short)
        update_dict(texts, text, lang, key.split('|')[0])
    return texts

def get_text_from_key(key: str, lang: str=None, format_args: list=None, short: bool=False) -> object:
    """
    Gets text based on a . delimited key string such as x.y.z
    """
    bigger_toks = key.split('|')
    key = bigger_toks[0]
    if len(bigger_toks) > 1:
        format_args = bigger_toks[1].split(',')
    toks = key.split('.')

    collection = toks[0]
    key_toks = toks[1:]

    wild_card = False
    if '*' in key_toks:
        key_toks = key_toks[:-1]
        wild_card = True

    _key = '.'.join(key_toks) or None
    text = None

    if wild_card:
        result = {}
        for _text in LanguageText.get_values(collection, _key):
            key = _text['id'].split('.')[-1] if _key is not None else _text['id']
            update_dict(result, _text, lang, key, short)
        return result

    else:
        text = LanguageText.get_value(collection, _key)

    if text is None:
        raise KeyError(f"Key: '{_key}' not found in '{collection}' collection")
    if 'short' in text:
        text = text['short'] if short else text['long']
    result =  get_translated_field(text, lang)
    if format_args is not None:
        result = result.format(*format_args)

    return result

def update_dict(result, text, lang, key: str=None, short: bool=False):
    primary_key = key or f"{text['id']}"
    toks = primary_key.split('.')
    while len(toks) > 1:
        _key = toks.pop(0)
        result[_key] = result.get(_key, {})
        result = result[_key]
    if isinstance(text, dict):
        if 'en' in text:
            _key = toks.pop(0)
            if isinstance(result, str):
                result = { 'long': result }
            current_result = result.get(_key)
            value = get_translated_field(text, lang or get_lang())
            if current_result is not None and 'short' in current_result:
                current_result['long'] = current_result.get('long', value)
                result[_key] = current_result['short'] if short else current_result['long']
            else:
                result[_key] = value
        else:
            result.update(text)
    else:
        _key = toks.pop(0)
        current_result = result.get(_key)
        if current_result is not None and 'short' in current_result:
            current_result['long'] = current_result.get('long', text)
            result[_key] = current_result
        else:
            result[_key] = text

def get_localized_text(category: str, name: str, /, format_args: list=None, sub_category: str=None, lang: str=None) -> str:
    """
    Retreives a sentence from the sentence dictionary, formatting it if necessary

    For regular categories returns a single string, if a wildcard is supplied then a
    dict is returned
    """
    collection = category

    _primary_key = '' if sub_category is None else f'{sub_category}.'

    wild_card = False
    if name == '*':
        # result = {}
        wild_card = True
    #    _primary_key = _primary_key or None
    #    for text in LanguageText.get_values(collection, _primary_key):
    #        update_dict(result, text, lang)
    #
    # else:
    result = get_text_from_key(f"{collection}.{_primary_key or ''}{name}", lang)
        # primary_key = f"{_primary_key or ''}{name}"
        # text = LanguageText.get_value(collection, primary_key)
        # result = get_translated_field(text, lang or get_lang())

    if format_args is not None and not wild_card:
        result = result.format(*format_args)

    return result
