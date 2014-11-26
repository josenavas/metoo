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

    @property
    def uri(self):
        return '/studies/%d' % self.id

class Type(BaseModel):
    uri = pw.CharField(unique=True) # TODO should this be TextField? we don't know how long these uris might be in practice

class Artifact(BaseModel):
    data = pw.BlobField()
    type = pw.ForeignKeyField(Type)
    study = pw.ForeignKeyField(Study)

class ArtifactProxy(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    artifact = pw.ForeignKeyField(Artifact)
    study = pw.ForeignKeyField(Study, related_name='artifacts')

    @property
    def uri(self):
        return '/studies/%d/artifacts/%d' % (self.study.id, self.id)

# TODO a study can have many workflows associated with it, but can a workflow
# be associated with many studies?
class Workflow(BaseModel):
    name = pw.CharField() # TODO should this be normalized?
    description = pw.TextField()
    template = pw.TextField()
    study = pw.ForeignKeyField(Study, related_name='workflows', null=True)

    @property
    def uri(self):
        return '/studies/%d/workflows/%d' % (self.study.id, self.id)

class WorkflowInput(BaseModel):
    class Meta:
        indexes = [(('key', 'workflow'), True)]

    name = pw.CharField()
    type = pw.ForeignKeyField(Type)
    default = pw.BlobField(null=True)
    workflow = pw.ForeignKeyField(Workflow, related_name='inputs')

# TODO how to handle inputs to the workflow?
class Job(BaseModel):
    status = pw.CharField(default='submitted') # TODO normalize
    submitted = pw.DateTimeField(default=datetime.datetime.now)
    completed = pw.DateTimeField(null=True)
    workflow = pw.ForeignKeyField(Workflow)
    study = pw.ForeignKeyField(Study, related_name='jobs')

    @property
    def uri(self):
        return '/studies/%d/jobs/%d' % (self.study.id, self.id)

class JobInput(BaseModel):
    class Meta:
        indexes = [(('job', 'key', 'order'), True)]
        order_by = ('job', 'key', 'order')


    key = pw.CharField()
    value = pw.BlobField()
    order = pw.IntegerField()
    job = pw.ForeignKeyField(Job, related_name='inputs')

def initialize_db():
    db.connect()
    db.create_tables(
        [Study, Artifact, ArtifactProxy, Type, Workflow, Job, JobInput], True)
    _populate_type_table()

def _populate_type_table():
    # circular imports FTW
    from qiime.types import type_registry

    for uri in type_registry.get_types():
        if Type.select().where(Type.uri == uri).count() == 0:
            Type(uri=uri).save()
