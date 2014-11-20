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
    study = pw.ForeignKeyField(Study, related_name='workflows', null=True)

# TODO how to handle inputs to the workflow template?
class Job(BaseModel):
    status = pw.CharField(default='submitted') # TODO normalize
    submitted = pw.DateTimeField(default=datetime.datetime.now)
    completed = pw.DateTimeField(null=True)
    workflow_template = pw.ForeignKeyField(WorkflowTemplate)
    study = pw.ForeignKeyField(Study, related_name='jobs')

class JobInputParameter(BaseModel):
    name = pw.CharField()
    value = pw.BlobField()
    job = pw.ForeignKeyField(Job, related_name='parameters')

class JobInputArtifact(BaseModel):
    class Meta:
        indexes = [(('order', 'job'), True)]
        order_by = ('order',)

    order = pw.IntegerField()
    list_id = pw.IntegerField(null=True)
    artifact = pw.ForeignKeyField(ArtifactProxy)
    job = pw.ForeignKeyField(Job, related_name='artifacts')

def initialize_db():
    db.connect()
    db.create_tables(
        [Study, Artifact, ArtifactProxy, ArtifactType, WorkflowTemplate,
         Job, JobInputParameter, JobInputArtifact], True)
    _populate_artifact_type_table()

def _populate_artifact_type_table():
    for type_ in plugin_registry.get_types():
        uri = type_.uri
        if ArtifactType.select().where(ArtifactType.uri == uri).count() == 0:
            ArtifactType(uri=uri).save()
