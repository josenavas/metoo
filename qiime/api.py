import qiime
from qiime.core.registry import plugin_registry
from qiime.core.tornadotools import route, GET, POST, PUT, DELETE, yield_urls
from qiime.db import Artifact, ArtifactProxy, Study, WorkflowTemplate, Job

def get_urls():
    return list(yield_urls())

@route('/system', GET)
def system_info():
    return {'version': qiime.__version__}

@route('/system/methods', GET, params=['plugin'])
def list_methods(plugin=None):
    return {'methods': [m.uri for m in plugin_registry.get_methods(plugin=plugin)]}

@route('/system/methods/:method', GET)
def method_info(method_uri):
    method = plugin_registry.get_method(method_uri)
    return {
        'uri': method.uri,
        'name': method.name,
        'help': method.docstring,
        'annotations': {
            'artifacts': [],  # (parameterized) artifacts (defined in org.qiime.plugins.[plugin-name].artifacts)
            'parameters': {}, # (parameterized) primitives (defined in org.qiime.types.primitives|parameterized)
            'return': []      # (parameterized) artifacts
        }
    }

@route('/system/plugins', GET)
def list_plugins():
    return {'plugins': list(plugin_registry.get_plugin_uris())}

@route('/system/plugins/:plugin', GET)
def plugin_info(plugin_uri):
    plugin = plugin_registry.get_plugin(plugin_uri)

    plugin_info = {
        'uri': plugin_uri,
        'name': plugin.name,
        'version': plugin.version,
        'author': plugin.author,
        'description': plugin.description
    }
    plugin_info.update(list_methods(plugin=plugin_uri))

    return plugin_info

@route('/studies', GET)
def list_studies():
    return {
        'studies': [study.id for study in Study.select()]
    }

@route('/studies', POST, params=['name', 'description'])
def create_study(request, name, description):
    study = Study(name=name, description=description)
    study.save()
    return {
        'study_id': study.id
    }

@route('/studies/:study', GET)
def study_info(study_id):
    study = Study.get(Study.id == study_id)

    return {
        'study_id': study.id,
        'name': study.name,
        'description': study.description,
        'created': str(study.created)
    }

@route('/studies/:study', PUT, params=['name', 'description'])
def study_info(request, study_id, name=None, description=None):
    study = Study.get(Study.id == study_id)
    if name is not None:
        study.name = name
    if description is not None:
        study.description = description
    study.save()

    return {} # TODO normalize responses with status

@route('/studies/:study', DELETE)
def study_info(study_id):
    study = Study.get(Study.id == study_id)
    study.delete_instance() # TODO think about cascading deletes

    return {} # TODO normalize responses with status

@route('/studies/:study/artifacts', POST, params=['name', 'artifact_type'])
def create_artifact(request, study_id, name, artifact_type):
    data = _get_file_data(request)
    if data is None:
        raise ValueError("Cannot create artifact: missing uploaded file.")

    # TODO remove when using postgresql and foreign keys are actually supported
    study = Study.get(id=study_id)
    artifact = Artifact(type=artifact_type, data=data, study=study)
    artifact.save()

    artifact_proxy = ArtifactProxy(name=name, artifact=artifact, study=study)
    artifact_proxy.save()

    return {
        'artifact_id': artifact_proxy.id
    }

@route('/studies/:study/artifacts', GET)
def list_artifacts(study_id):
    artifacts = Study.get(id=study_id).artifacts

    return {
        'artifact_ids': [a.id for a in artifacts]
    }

@route('/studies/:study/artifacts', PUT, params=['artifact_id'])
def link_artifact(request, study_id, artifact_id):
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
        'artifact_id': linked_artifact.id
    }

@route('/studies/:study/artifacts/:artifact', GET, params=['export'])
def artifact_info(study_id, artifact_id, export=None):
    proxy = ArtifactProxy.select().where(
        ArtifactProxy.id == artifact_id,
        ArtifactProxy.study == study_id).get()

    return {
        'arifact_id': proxy.id,
        'name': proxy.name,
        'type': proxy.artifact.type
    }

@route('/studies/:study/artifacts/:artifact', PUT, params=['name'])
def update_artifact(request, study_id, artifact_id, name=None):
    proxy = ArtifactProxy.get(id=artifact_id)
    if proxy.study.id == int(study_id): # TODO fix int hack!
        if name is not None:
            proxy.name = name

        proxy.save()
    else:
        raise ValueError("Wrong study")

    return {}

@route('/studies/:study/artifacts/:artifact', DELETE)
def delete_artifact(study_id, artifact_id):
    proxy = ArtifactProxy.get(id=artifact_id)
    if proxy.study.id == int(study_id): # TODO fix int hack!
        proxy.delete_instance()
    else:
        raise ValueError("Wrong study")

    return {}

@route('/studies/:study/jobs', GET, params=['status'])
def list_jobs(study_id, status=None):
    jobs = Study.get(id=study_id).jobs

    if status is not None:
        jobs = jobs.where(Job.status == status)

    return {
        'job_ids': [j.id for j in jobs]
    }

@route('/studies/:study/jobs', POST, params=['workflow_id'])
def create_job(request, study_id, workflow_id):
    job = Job(workflow_template=workflow_id, study=study_id)
    job.save()

    return {
        'job_id': job.id
    }

@route('/studies/:study/jobs/:job', GET, params=['subscribe'])
def job_info(study_id, job_id, subscribe=None): # TODO handle SSE
    job = Job.get(id=job_id)

    return {
        'job_id': job.id,
        'status': job.status,
        'submitted': str(job.submitted),
        'workflow_id': job.workflow_template.id,
    }

# TODO handle updating downstream parts of the workflow
@route('/studies/:study/jobs/:job', PUT, params=['status'])
def update_job(request, study_id, job_id, status=None):
    job = Job.get(id=job_id)

    # TODO do something smarter here
    if status is not None:
        job.status = status

    job.save()

    return {}

@route('/studies/:study/jobs/:job', DELETE)
def terminate_job(study_id, job_id):
    job = Job.get(id=job_id)
    job.status = 'terminated'
    job.save()

    return {}

@route('/studies/:study/workflows', GET)
def list_workflow_templates(study_id):
    templates = Study.get(id=study_id).workflows

    return {
        'workflow_ids': [t.id for t in templates]
    }

@route('/studies/:study/workflows', POST,
       params=['name', 'description', 'template'])
def create_workflow_template(request, study_id, name, description, template):
    template = WorkflowTemplate(name=name, description=description,
                                template=template, study=study_id)
    template.save()

    return {
        'workflow_id': template.id
    }

@route('/studies/:study/workflows/:workflow', GET)
def workflow_template_info(study_id, workflow_id):
    template = WorkflowTemplate.get(id=workflow_id)

    return {
        'workflow_id': template.id,
        'name': template.name,
        'description': template.description,
        'template': template.template
    }

@route('/studies/:study/workflows/:workflow', PUT,
       params=['name', 'description', 'template'])
def update_workflow_template(request, study_id, workflow_id, name=None,
                             description=None, template=None):
    workflow_template = WorkflowTemplate.get(id=workflow_id)

    if name is not None:
        workflow_template.name = name
    if description is not None:
        workflow_template.description = description
    if template is not None:
        workflow_template.template = template

    workflow_template.save()

    return {}

@route('/studies/:study/workflows/:workflow', DELETE)
def delete_workflow_template(study_id, workflow_id):
    template = WorkflowTemplate.get(id=workflow_id)

    if template.study.id == int(study_id): # TODO fix int hack!
        template.delete_instance()
    else:
        raise ValueError("Wrong study")

    return {}

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
