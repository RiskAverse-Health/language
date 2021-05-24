"""
Methods for getting localized text
"""
import os
import json
import codecs

from typing import List, Dict

from .connection import init_db, get_db
from .models import LanguageText

DEFAULT_LANGUAGE_HOST =  'mongodb://localhost:27017/language'
init_db(os.environ.get('LANGUAGE_URI', DEFAULT_LANGUAGE_HOST))

context = {}

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

def get_texts_from_key_list(keys: List[str], lang: str=None) -> Dict[str, object]:
    """
    Gets texts based on a list of keys. Returned dict puts text nested in order determined by the key
    """
    texts = {}
    for key in keys:
        text = get_text_from_key(key, lang=lang or get_lang())
        toks = key.split('.')
        current = texts
        prev = current

        for i, tok in enumerate(toks):
            is_last = (i == len(toks) - 1)
            if tok == '*':
                prev[toks[i - 1]] = text
            elif tok not in current:
                current[tok] = text if is_last else {}

            if is_last:
                # We're at a leaf node so break since we have the text
                break

            # If we're not done then keep going deeper
            prev = current
            current = current[tok]

    return texts

def get_text_from_key(key: str, lang: str=None, format_args=None) -> object:
    """
    Gets text based on a . delimited key string such as x.y.z
    """
    toks = key.split('.')
    collection = toks[0]
    key = '.'.join(toks[1:])

    text = '<<<N/A>>>'

    text = LanguageText.get_text(collection, key)
    if text is None:
        raise KeyError(f'Key: {key} not found in {collection} collection')
    return get_translated_field(text, lang)

def get_localized_text(category: str, name: str, /, format_args: list=None, sub_category: str=None, lang: str=None) -> str:
    """
    Retreives a sentence from the sentence dictionary, formatting it if necessary

    For regular categories returns a single string, if a wildcard is supplied then a
    dict is returned
    """
    data = sentences[category]

    result = None
    container = None
    if sub_category is None:
        container = data
    else:
        container = data[sub_category]

    wild_card = False
    if name == '*':
        result = {}
        wild_card = True
        #result = {key: val[lang] for key, val in container.items()}
        for key, val in container.items():
            if 'en' in val:
                # Leaf node, just add text
                result[key] = val[lang or get_lang()]
            else:
                # There are sub categories, so loop through them all
                result[key] = {sub_key: sub_val[lang] for sub_key, sub_val in val.items()}
    else:
        result = container.get(name)
        if result is None and sub_category is not None:
            container = data
        result = container[name][lang or get_lang()]

    if format_args is not None and not wild_card:
        result = result.format(*format_args)

    return result
