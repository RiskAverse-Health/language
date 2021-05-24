from mongoengine import Document
from mongoengine.fields import StringField

class LanguageText(Document):
    id = StringField(primary_key=True)
    en = StringField()
    es = StringField()
