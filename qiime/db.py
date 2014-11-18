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
    type = pw.CharField() # TODO normalize
    data = pw.BlobField()
    study = pw.ForeignKeyField(Study)

class ArtifactProxy(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    artifact = pw.ForeignKeyField(Artifact)
    study = pw.ForeignKeyField(Study, related_name='artifacts')

class WorkflowTemplate(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    description = pw.TextField()
    template = pw.TextField()
    study = pw.ForeignKeyField(Study, related_name='workflows')

def initialize_db():
    db.connect()
    db.create_tables([Study, Type, Artifact, ArtifactProxy, WorkflowTemplate],
                     True)
