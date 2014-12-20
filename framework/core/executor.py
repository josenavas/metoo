from framework.core.registry import plugin_registry
from framework.core.util import extract_artifact_id, listify_duplicate_keys
from framework.types import Artifact, Parameterized, Primitive
from framework.types.parameterized import List, ChooseMany
import framework.db as db

import datetime

class Executor(object):
    def __init__(self, job):
        self.job = job

    def __call__(self):
        method_uri = self.job.workflow.template # TODO currently the template is just the method

        method = plugin_registry.get_plugin(method_uri).get_method(method_uri)
        study = self.job.study.id
        inputs = listify_duplicate_keys(self.job.inputs)

        results = method(study, **inputs)
        for i, (result, output) in enumerate(zip(results, method.outputs)):
            ordered_result = traverse_result_and_record(result, output)
            db.JobOutput(job=self.job, order=i, result=ordered_result).save()

        self.job.status = 'completed'
        self.job.completed = datetime.datetime.now()
        self.job.save()

def traverse_result_and_record(result, type_, order=0, parent=None):
    if issubclass(type_, Artifact):
        ordered_result = db.OrderedResult(order=order,
                                          parent=parent,
                                          artifact=db.ArtifactProxy.get(db.ArtifactProxy.id == extract_artifact_id(result)))
        ordered_result.save()
        return ordered_result

    if issubclass(type_, Primitive):
        ordered_result = db.OrderedResult(order=order,
                                          parent=parent,
                                          primitive=result)
        ordered_result.save()
        return ordered_result

    if type_.name == 'List' or type_.name == 'ChooseMany':
        parent = db.OrderedResult(order=order, parent=parent)
        parent.save()
        for i, r in enumerate(result):
            traverse_result_and_record(r, type_.subtype, order=i, parent=parent)
        return parent

    return traverse_result_and_record(result, type_.subtype, order=order, parent=parent)
