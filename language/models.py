from mongoengine import Document
from mongoengine.fields import StringField
from mongoengine.queryset import QuerySet

from .connection import get_db

class LanguageText(Document):
    id = StringField(primary_key=True)
    en = StringField()
    es = StringField()

    def to_dict(self):
        _language_text = self.to_mongo()
        _language_text.update({'id': _language_text.pop('_id')})
        return _language_text

    @classmethod
    def get_value(cls, collection, key):
        collection = get_db()[collection]
        queryset = QuerySet(cls, collection)
        language_text =  queryset(id=key).first()
        if language_text is None:
            return None
        return language_text.to_mongo()

    @classmethod
    def get_values(cls, collection, key):
        query = {}
        print(collection)
        if key is not None:
            query.update({'id__icontains': key})
        collection = get_db()[collection]
        queryset = QuerySet(cls, collection)
        language_text =  queryset(**query)
        return list([lt.to_dict() for lt in language_text])
