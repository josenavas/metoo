import datetime

import peewee as pw
# this won't be necessary for postgresql
# ... also very creepy
from playhouse.sqlite_ext import PrimaryKeyAutoIncrementField

from qiime.core.registry import plugin_registry

db = pw.SqliteDatabase('qiime2.db')

class BaseModel(pw.Model):
    id = PrimaryKeyAutoIncrementField()

    class Meta:
        database = db

class Study(BaseModel):
    name = pw.CharField()
    description = pw.TextField()
    created = pw.DateTimeField(default=datetime.datetime.now)

class ArtifactType(BaseModel):
    uri = pw.CharField(unique=True) # TODO should this be TextField? we don't know how long these uris might be in practice

class Artifact(BaseModel):
    data = pw.BlobField()
    type = pw.ForeignKeyField(ArtifactType)
    study = pw.ForeignKeyField(Study)

class ArtifactProxy(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    artifact = pw.ForeignKeyField(Artifact)
    study = pw.ForeignKeyField(Study, related_name='artifacts')

# TODO a study can have many workflow templates associated with it, but can a
# workflow template be associated with many studies?
class WorkflowTemplate(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    description = pw.TextField()
    template = pw.TextField()
    study = pw.ForeignKeyField(Study, related_name='workflows')

# TODO how to handle inputs to the workflow template?
class Job(BaseModel):
    status = pw.CharField(default='submitted') # TODO normalize
    submitted = pw.DateTimeField(default=datetime.datetime.now)
    workflow_template = pw.ForeignKeyField(WorkflowTemplate)
    study = pw.ForeignKeyField(Study, related_name='jobs')

def initialize_db():
    db.connect()
    db.create_tables(
        [Study, Artifact, ArtifactProxy, ArtifactType, WorkflowTemplate,
         Job], True)
    _populate_artifact_type_table()

def _populate_artifact_type_table():
    # TODO when to repopulate? currently reqires db to be wiped each time
    for type_ in plugin_registry.get_types():
        ArtifactType(uri=type_.uri).save()
