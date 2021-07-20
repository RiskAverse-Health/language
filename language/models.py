"""
Models for Language library
"""
from mongoengine import Document
from mongoengine.fields import StringField
from mongoengine.queryset import QuerySet

from language.connection import get_db

class LanguageText(Document):
    id = StringField(primary_key=True)
    en = StringField()
    es = StringField()

    meta = {'db_alias': 'language'}

    def to_dict(self):
        """
        Returns dict representation of object
        """
        _language_text = self.to_mongo()
        _language_text.update({'id': _language_text.pop('_id')})
        return _language_text

    @classmethod
    def get_value(cls, collection, key):
        """
        Gets first value matching id from collection
        """
        # collection = get_db()[collection]
        # queryset = QuerySet(cls, collection)
        # language_text =  queryset('id_contains'=key)
        # if language_text is None:
        #     return None
        language_text = cls.get_values(collection, key)
        if language_text is None:
            return None
        if len(language_text) == 1:
            return language_text[0]
        all_text = {
            lt['id'].replace(key, '').replace('.', ''): lt
            for lt in language_text
        }
        if 'short' in all_text:
            return {
                'short': all_text['short'],
                'long': all_text.get('long') or all_text.get('') or None or all_text['short']
            }
        return language_text[0]

    @classmethod
    def get_values(cls, collection, key):
        """
        Gets list of object matching key
        """
        query = {}
        if key is not None:
            query.update({'id__icontains': key})
        collection = get_db()[collection]
        queryset = QuerySet(cls, collection)
        language_text =  queryset(**query)
        if language_text is None:
            return None
        return list([lt.to_dict() for lt in language_text])
