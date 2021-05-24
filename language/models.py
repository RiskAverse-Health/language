from mongoengine import Document
from mongoengine.fields import StringField
from mongoengine.queryset import QuerySet

from .connection import get_db

class LanguageText(Document):
    id = StringField(primary_key=True)
    en = StringField()
    es = StringField()

    @classmethod
    def get_text(cls, collection, key):
        collection = get_db()[collection]
        queryset = QuerySet(cls, collection)
        language_text =  queryset(id=key).first()
        if language_text is None:
            return None
        return language_text.to_mongo()
