import datetime

import peewee as pw
# this won't be necessary for postgresql
# ... also very creepy
from playhouse.sqlite_ext import PrimaryKeyAutoIncrementField

db = pw.SqliteDatabase('qiime2.db')

class BaseModel(pw.Model):
    id = PrimaryKeyAutoIncrementField()

    class Meta:
        database = db

class Study(BaseModel):
    name = pw.CharField()
    description = pw.TextField()
    created = pw.DateTimeField(default=datetime.datetime.now)

class Type(BaseModel):
    name = pw.CharField()

class Artifact(BaseModel):
    name = pw.CharField()
    type = pw.ForeignKeyField(Type)
    parent = pw.ForeignKeyField('self', null=True)
    data = pw.BlobField(
        null=True,
        constraints=[
            pw.Check('(artifact.data IS NOT NULL AND'
                     ' artifact.parent_id IS NULL) OR '
                     '(artifact.data IS NULL AND'
                     ' artifact.parent_id IS NOT NULL)')])
    study = pw.ForeignKeyField(Study, related_name='artifacts')

def initialize_db():
    db.connect()
    db.create_tables([Study, Type, Artifact], True)
