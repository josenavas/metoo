import inspect

import framework
from framework.core.executor import Executor
from framework.core.registry import plugin_registry
from framework.core.tornadotools import route, GET, POST, PUT, DELETE, yield_urls
from framework.core.util import extract_artifact_id, listify_duplicate_keys
from framework.db import Artifact, ArtifactProxy, Type, Study, Workflow, WorkflowInput, Job, JobInput, OrderedResult
from framework.types import type_registry

def get_urls():
    return list(yield_urls())

@route('/system', GET)
def system_info(request_handler):
    return {
        'version': framework.__version__
    }

@route('/system/plugins', GET)
@route('/system/plugins/all', GET)
def list_plugins(request_handler):
    return {
        'plugins': list(plugin_registry.get_plugin_uris())
    }

@route('/system/plugins/:plugin', GET)
def plugin_info(request_handler, plugin_name):
    plugin = plugin_registry.get_plugin(plugin_name)

    return {
        'name': plugin.name,
        'version': plugin.version,
        'author': plugin.author,
        'description': plugin.description
    }

@route('/system/plugins/all/methods', GET)
def list_all_methods(request_handler):
    return list_methods(request_handler, None)

@route('/system/plugins/:plugin/methods', GET)
def list_methods(request_handler, plugin_name):
    return {'methods': [m.uri for m in plugin_registry.get_methods(plugin_name=plugin_name)]}

@route('/system/plugins/:plugin/methods/:method', GET)
def method_info(request_handler, plugin_name, method_name):
    method = plugin_registry.get_plugin(plugin_name).get_method(method_name)

    return {
        'name': method.name,
        'help': method.docstring,
        'inputs': {name: cls.annotation() for name, cls in method.inputs.items()},
        'outputs': [cls.annotation() for cls in method.outputs]
    }

@route('/system/plugins/all/types', GET, params=['format'])
def list_all_plugin_types(request_handler, format=None):
    return list_plugin_types(request_handler, None, format=format)

@route('/system/plugins/:plugin/types', GET, params=['format'])
def list_plugin_types(request_handler, plugin_name, format=None):
    if format is None:
        format = 'list'

    types = plugin_registry.get_types(plugin_name=plugin_name)

    if format == 'list':
        return {
            'types': [t.uri for t in types]
        }
    elif format == 'tree':
        cls_tree = inspect.getclasstree([t for t in types])
        return _list_tree_to_dict_tree(cls_tree) # TODO use better JSON tree representation
    else:
        raise ValueError("Unrecognized format: %r" % format)

@route('/system/plugins/:plugin/types/:type', GET)
@route('/system/types/primitives/:type', GET)
@route('/system/types/parameterized/:type', GET)
def type_info(request_handler, *_):
    type_ = type_registry.get_type(request_handler.request.path)

    return {
        'name': type_.name,
        'description': type_.__doc__
    }

@route('/system/types/primitives', GET)
def list_primitive_types(request_handler):
    return {
        'primitives': [t.uri for t in type_registry.get_primitive_types().values()]
    }

@route('/system/types/parameterized', GET)
def list_parameterized_types(request_handler):
    return {
        'parameterized': [t.uri for t in
                  type_registry.get_parameterized_types().values()]
    }

@route('/studies', GET)
def list_studies(request_handler):
    return {
        'studies': [study.uri for study in Study.select()]
    }

@route('/studies', POST, params=['name', 'description'])
def create_study(request_handler, name, description):
    study = Study(name=name, description=description)
    study.save()
    return {
        'study': study.uri
    }

@route('/studies/:study', GET)
def study_info(request_handler, study_id):
    study = Study.get(Study.id == study_id)

    return {
        'name': study.name,
        'description': study.description,
        'created': str(study.created)
    }

@route('/studies/:study', PUT, params=['name', 'description'])
def study_info(request_handler, study_id, name=None, description=None):
    study = Study.get(Study.id == study_id)
    if name is not None:
        study.name = name
    if description is not None:
        study.description = description
    study.save()

    return {}

@route('/studies/:study', DELETE)
def study_info(request_handler, study_id):
    study = Study.get(Study.id == study_id)
    study.delete_instance() # TODO think about cascading deletes

    return {}

@route('/studies/:study/artifacts', POST, params=['name', 'artifact_type'])
def create_artifact(request_handler, study_id, name, artifact_type):
    data = _get_file_data(request_handler.request)
    if data is None:
        raise ValueError("Cannot create artifact: missing uploaded file.")

    # TODO remove when using postgresql and foreign keys are actually supported
    study = Study.get(id=study_id)
    type_ = Type.get(uri=artifact_type)
    artifact = Artifact(type=type_, data=data, study=study)
    artifact.save()

    artifact_proxy = ArtifactProxy(name=name, artifact=artifact, study=study)
    artifact_proxy.save()

    return {}

@route('/studies/:study/artifacts', GET)
def list_artifacts(request_handler, study_id):
    artifacts = Study.get(id=study_id).artifacts

    return {
        'artifacts': [a.uri for a in artifacts]
    }

@route('/studies/:study/artifacts', PUT, params=['artifact'])
def link_artifact(request_handler, study_id, artifact):
    artifact_id = extract_artifact_id(artifact)
    parent_artifact = ArtifactProxy.get(id=artifact_id)
    linked_artifacts = ArtifactProxy.select().where(
        ArtifactProxy.artifact == parent_artifact.artifact,
        ArtifactProxy.study == study_id)

    if linked_artifacts.count() == 0:
        linked_artifact = ArtifactProxy(artifact=parent_artifact.artifact,
                                        name=parent_artifact.name,
                                        study=study_id)
        linked_artifact.save()
    else:
        linked_artifact = linked_artifacts.get()

    return {
        'artifact': linked_artifact.uri
    }

@route('/studies/:study/artifacts/:artifact', GET, params=['export'])
def artifact_info(request_handler, study_id, artifact_id, export=None):
    proxy = ArtifactProxy.select().where(
        ArtifactProxy.id == artifact_id,
        ArtifactProxy.study == study_id).get()

    # TODO chunked downloading, figure out recommended file extension, support
    # multiple export formats
    if export:
        # don't return anything because we're handling the writing of the
        # request here
        filename = '"%s.txt"' % proxy.name
        data = proxy.artifact.data
        request_handler.set_header('Content-Type', 'application/octet-stream')
        request_handler.set_header('Content-Disposition',
                                   'attachment; filename=%s' % filename)
        request_handler.write(data)
    else:
        return {
            'name': proxy.name,
            'type': proxy.artifact.type.uri
        }

@route('/studies/:study/artifacts/:artifact', PUT, params=['name'])
def update_artifact(request_handler, study_id, artifact_id, name=None):
    proxy = ArtifactProxy.get(id=artifact_id)
    if proxy.study.id == int(study_id): # TODO fix int hack!
        if name is not None:
            proxy.name = name

        proxy.save()
    else:
        raise ValueError("Wrong study")

    return {}

@route('/studies/:study/artifacts/:artifact', DELETE)
def delete_artifact(request_handler, study_id, artifact_id):
    proxy = ArtifactProxy.get(id=artifact_id)
    if proxy.study.id == int(study_id): # TODO fix int hack!
        proxy.delete_instance()
    else:
        raise ValueError("Wrong study")

    return {}

@route('/studies/:study/jobs', GET, params=['status'])
def list_jobs(request_handler, study_id, status=None):
    jobs = Study.get(id=study_id).jobs

    if status is not None:
        jobs = jobs.where(Job.status == status)

    return {
        'jobs': [j.uri for j in jobs]
    }

@route('/studies/:study/jobs', POST, params=['workflow', 'method'])
def create_job(request_handler, study_id, workflow=None, method=None):
    if workflow is None and method is None:
        raise Exception()
    if method is not None and workflow is not None:
        raise Exception()

    if workflow is not None:
        raise NotImplementedError()

    if method is not None:
        template, name, desc = _generate_workflow_template_from_method(method)
        workflow = Workflow(study=study_id, template=template, name=name,
                            description=desc)
        workflow.save()

        job = Job(workflow=workflow, study=study_id)
        job.save()

        method = plugin_registry.get_plugin(method).get_method(method)

        # TODO fix this paypal hack
        request = request_handler.request
        for param in request.arguments:
            # :tears:
            if param.startswith('input_'):
                _, key = param.split('input_')
                value = request.arguments[param]
                for i, v in enumerate(value):
                    job_input = JobInput(key=key, value=v, job=job, order=i)
                    job_input.save()

        # TODO we don't want to fire off the job here b/c this will block
        # tornado
        Executor(job)()

        return {
            'job': job.uri
        }

@route('/studies/:study/jobs/:job', GET, params=['subscribe'])
def job_info(request_handler, study_id, job_id, subscribe=None): # TODO handle SSE
    if subscribe is not None:
        raise NotImplementedError()

    job = Job.get(id=job_id)
    completed = job.completed
    outputs = None
    if completed is not None:
        completed = str(completed)
        outputs = [_construct_list(o.result) for o in job.outputs]

    return {
        'status': job.status,
        'submitted': str(job.submitted),
        'completed': completed,
        'workflow': job.workflow.uri,
        # TODO track defaults as well. How do we do this for workflows?
        'inputs': listify_duplicate_keys(job.inputs, decode_to_str=True),
        'outputs': outputs
    }

# TODO handle updating downstream parts of the workflow
@route('/studies/:study/jobs/:job', PUT, params=['status'])
def update_job(request_handler, study_id, job_id, status=None):
    job = Job.get(id=job_id)

    # TODO do something smarter here
    if status is not None:
        job.status = status

    job.save()

    return {}

@route('/studies/:study/jobs/:job', DELETE)
def terminate_job(request_handler, study_id, job_id):
    job = Job.get(id=job_id)
    job.status = 'terminated'
    job.save()

    return {}

@route('/studies/:study/workflows', GET)
def list_workflows(request_handler, study_id):
    workflows = Study.get(id=study_id).workflows

    return {
        'workflows': [w.uri for w in workflows]
    }

@route('/studies/:study/workflows', POST,
       params=['name', 'description', 'template'])
def create_workflow(request_handler, study_id, name, description, template):
    workflow = Workflow(name=name, description=description, template=template,
                        study=study_id)
    workflow.save()

    return {
        'workflow': workflow.uri
    }

@route('/studies/:study/workflows/:workflow', GET)
def workflow_info(request_handler, study_id, workflow_id):
    workflow = Workflow.get(id=workflow_id)

    return {
        'name': workflow.name,
        'description': workflow.description,
        'template': workflow.template
    }

@route('/studies/:study/workflows/:workflow', PUT,
       params=['name', 'description', 'template'])
def update_workflow(request_handler, study_id, workflow_id, name=None,
                    description=None, template=None):
    workflow = Workflow.get(id=workflow_id)

    if name is not None:
        workflow.name = name
    if description is not None:
        workflow.description = description
    if template is not None:
        workflow.template = template

    workflow.save()

    return {
        'workflow': workflow.uri
    }

@route('/studies/:study/workflows/:workflow', DELETE)
def delete_workflow(request_handler, study_id, workflow_id):
    workflow = Workflow.get(id=workflow_id)

    if workflow.study.id == int(study_id): # TODO fix int hack!
        workflow.delete_instance()
    else:
        raise ValueError("Wrong study")

    return {}

def _list_tree_to_dict_tree(list_tree):
    tree = {}
    uri = None
    for entry in list_tree:
        if isinstance(entry, tuple):
            cls = entry[0]
            if hasattr(cls, 'uri') and cls.uri is not None:
                uri = cls.uri
            else:
                uri = cls.__name__
            subtree = {}
        else:
            # list of subclass entries
            subtree = _list_tree_to_dict_tree(entry)

        if uri is None:
            # shouldn't be possible to get here...
            raise ValueError("Subclass entries were not preceded by a "
                             "superclass entry.")
        tree[uri] = subtree
    return tree

def _get_file_data(request):
    files = request.files
    if not files:
        return None

    if len(files) > 1:
        raise ValueError("Need 1 named file to upload as artifact, found %d."
                         % len(files))

    upload_name, file_infos = files.popitem()
    if len(file_infos) != 1:
        raise ValueError("Need exactly 1 file to upload as artifact, found "
                         "named file %s with %d payloads." %
                         (repr(upload_name), len(file_infos)))
    file_info = file_infos[0]
    return file_info['body'] # bytes

def _generate_workflow_template_from_method(method_uri):
    # TODO finish me! :please:
    return method_uri, method_uri, method_uri

def _construct_list(ordered_result):
    if ordered_result.artifact is not None:
        return ordered_result.artifact.uri

    if ordered_result.primitive is not None:
        return ordered_result.primitive

    return [_construct_list(r) for r in ordered_result.children]
