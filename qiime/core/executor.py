from qiime.core.registry import plugin_registry
from qiime.core.util import is_list

class Executor(object):
    def __init__(self, job):
        self.job = job

    def __call__(self):
        method_uri = self.job.workflow.template # TODO currently the template is just the method

        method = plugin_registry.get_plugin(method_uri).get_method(method_uri)
        study = self.job.study.id
        inputs = listify_duplicate_keys(self.job.inputs)

        results = method(study, **inputs)
        print(results)


def listify_duplicate_keys(job_inputs):
    inputs = {}
    for input_ in job_inputs:
        key = input_.key
        if key in inputs:
            if is_list(inputs[key]):
                inputs[key].append(input_.value)
            else:
                inputs[key] = [inputs[key], input_.value]
        else:
            inputs[key] = input_.value
    return inputs
