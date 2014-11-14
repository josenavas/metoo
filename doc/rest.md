# QIIME 2 REST API

## /system

### GET
QIIME server version

## /system/methods

### GET
List of methods. Default is all methods across all plugins. Query parameter ``plugin`` will limit results to the specified plugin.

## /system/methods/:method

### GET
Information about the method, e.g., name, description, annotations, etc.

## /system/plugins

### GET
List of plugins.

## /system/plugins/:plugin

### GET
Info about the plugin, e.g., author, description, if its an official plugin, etc.

## /study

### GET
List studies you have access to.

### POST
Create a new study.

## /study/:study

### GET
Information about the study, e.g., name, description, creation time, etc.

### PUT
Update an existing study.

### DELETE
Delete an existing study.

## /study/:study/artifacts

### GET
Provide artifact abstract file system tree.

### POST
Create a new artifact.

### PUT
Link an existing artifact.

## /study/:study/artifacts/:artifact

### GET
Information about the artifact. Query parameter ``export`` specifies
file type to export artifact as for downloading.

### PUT
Update artifact metadata, e.g., name, description. History, underlying data, and
type cannot be modified.

### DELETE
Delete artifact.

## /study/:study/jobs

### GET
List all jobs. Query parameter to filter by job status (completed, running,
etc.)

### POST
Create a new job.

## /study/:study/jobs/:job

### GET
Information about the job, e.g., status. SSE will also happen here via a query
parameter (``subscribe``).

### PUT
Update the job: pause, resume, or update a downstream parameter.

### DELETE
Terminate the job.

## /study/:study/workflows

### GET
List all workflow templates.

### POST
Create a new workflow template.

## /study/:study/workflows/:workflow

### GET
Return workflow template and metadata.

### PUT
Update workflow template and metadata.

### DELETE
Delete workfow template and metadata.
