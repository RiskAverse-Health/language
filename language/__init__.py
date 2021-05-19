"""
Methods for getting localized text
"""
import os
import json
import codecs

from typing import List, Dict

BASE_FOLDER = os.path.dirname(os.path.realpath(__file__))
LANGUAGE_FOLDER = os.path.join(BASE_FOLDER, 'static', 'language')

context = {}

def set_lang(lang: str):
    print(lang)
    context['lang'] = lang

def get_lang():
    return context.get('lang', 'en')

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
    text = '<<<N/A>>>'
    if len(toks) == 2:
        text = get_localized_text(toks[0], toks[1], lang=lang or get_lang(), format_args=format_args)
    elif len(toks) == 3:
        text = get_localized_text(toks[0], toks[2], sub_category=toks[1], lang=lang or get_lang(), format_args=format_args)

    return text

def get_localized_text(category: str, name: str, /, format_args: list=None, sub_category: str=None, lang: str=None) -> str:
    """
    Retreives a sentence from the sentence dictionary, formatting it if necessary

    For regular categories returns a single string, if a wildcard is supplied then a
    dict is returned
    """
    print(category, name, format_args, sub_category, lang)
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
