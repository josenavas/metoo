QIIME2
======

[![Build Status](https://travis-ci.org/biocore/metoo.png?branch=master)](https://travis-ci.org/biocore/metoo) [![Coverage Status](https://coveralls.io/repos/biocore/metoo/badge.png)](https://coveralls.io/r/biocore/metoo)

*Staging ground for QIIME2 development*

This repository serves as a staging ground for the next major version of
[QIIME](http://qiime.org/) (i.e., QIIME2), which will be a complete redesign
and reimplementation of the package.

**Note:** This repository exists mainly for developers and is not intended for
production. It will be transitioned to the canonical QIIME repo
([biocore/qiime](https://github.com/biocore/qiime)) when the package is ready
to be released. This package is under active development and all functionality
should be treated as **pre-alpha**.

# QIIME2 Proposed Roadmap
We propose a complete re-envisioning and redesign of QIIME from the ground up,
hereby referred to as QIIME2. In this document, we provide a concise and
high-level overview of various aspects of the QIIME2 project and how they differ
from the current QIIME software package.

**Note:** This summary is a **proposal** of high-level ideas that will guide the
design and implementation of QIIME2. We are soliciting input from all QIIME
developers and the QIIME user community via the QIIME forum. **Nothing is
finalized and everything is
subject to change.** Once we reach agreement on the project's direction and
vision, we will provide additional documents with further details
(e.g., requirements and design documents).

The roadmap is meant to provide a high-level view of the QIIME2. **It does not
contain specific implementation details.** For example, we may mention the use
of a database, but we're not yet defining the database schema or assuming use
of a particular database implementation (e.g., PostgreSQL).

This document was originally prepared based on conversations between
@gregcaporaso, @ebolyen, and @jairideout.

## Aspects of QIIME2

### Client-Server Architecture
QIIME2 will use a client-server architecture, allowing it to provide a graphical
interface (this will also enable multiple arbitrary interfaces, e.g., CLI, iPad,
BaseSpace). This architecture is supported in a single host (e.g. laptop or
VirtualBox) and multi-host deployment (e.g. a cluster or EC2). **All
interactions** with QIIME2 will happen through a standardized protocol provided
by the server (_qiime-server_). The goal of the protocol is to reduce complexity
and duplication in defining multiple interfaces. Additionally it will allow
remote execution over a network barrier (this would have been difficult to
achieve with [pyqi](http://pyqi.readthedocs.org/en/latest/)).

### Workers
Once the _qiime-server_ has received a request via the protocol, it will launch
a worker job to perform the computation. The _qiime-server_ will provide status
updates to clients through the protocol. The worker job will record the results
as an _artifact_ in a database.

### Database
**Note: This is not intended to be a substitute for the QIIME database
project (QiiTA).** This is a discussion of how data will be organized and stored
internally in QIIME2.

The database represents a significant departure from the way QIIME currently
handles data (e.g. storing input and output files in a directory structure).
Presently, data is serialized and deserialized to and from the file-system at
each step in an analysis. The resulting data are highly denormalized; for
example, sample IDs are duplicated throughout nearly every file format used in
QIIME. This gives rise to a number of issues. For example, it is very difficult
and error-prone to rename a sample ID after sequences have been demultiplexed.

Since QIIME fundamentally deals with samples at every step in an analysis, they
will become the basis of structuring output in a normalized way. The database
will store this normalized data as _artifacts_. _artifacts_ are data which are
analogous to QIIME's input and output files, but annotated with additional
metadata (e.g., history/provenance, semantic type, etc.). An _artifact_ can be
data that has been imported into QIIME2 (e.g., raw sequence data), or output
produced during an analysis (e.g., a UniFrac distance matrix). _artifacts_ can
be exported in a variety of file formats (e.g., for use in external tools, to
share with collaborators, or include in a publication).

### Graphical Interface (Web-based)
Currently it is very difficult to create custom workflows in QIIME; only a few
core developers are able to, and it leads to messy and error-prone code that is
difficult to maintain and validate with unit tests. Current QIIME workflows are
essentially black boxes: many users have voiced concern (e.g., on the QIIME
forum and at workshops) that they don't know the exact steps a workflow is
performing. Users have also been asking for a graphical way to perform QIIME
analyses since QIIME's first release; this is likely the most popular request
we've received, and it would significantly cut down the support burden on the
QIIME forum.

To address these concerns, we propose an easy-to-use, portable web-based
interface as the primary way to interact with QIIME2. The web-interface will not
merely wrap a command line interface (as we attempted with pyqi), but instead
will provide a powerful workflow-centered interaction model for both technical
and non-technical users. The interface will allow users to easily create
arbitrary workflows by dragging and dropping methods together. They will be
guided by a strong semantic type system to prevent easily-avoided errors such as
passing pre-split-libraries sequence data into OTU picking workflows. Users will
then be able to preview, export, download, visualize, and view the history of
their data as it becomes available. Additionally they may be able to query their
results like a database (because they are stored in one).

### Semantic Type System
All inputs and outputs of methods and workflows are _artifacts_. All
_artifacts_ have a semantic type. This allows inference and simple
validation when creating analyses (e.g., showing a user what methods/workflows
can be applied to an _artifact_).

There are two kinds of types: _abstract_ and _concrete_ types. An _abstract_
type is a group or collection of _concrete_ types that share a common interface.
A _concrete_ type is specific flavor of an _abstact_ type. Two _artifacts_ of
different _abstract_ types are never considered equivalent because they may not
have compatible interfaces, whereas two _artifacts_ of the same _abstract_ type
but different _concrete_ types may be considered equivalent, though would
warn the user that they may be providing a semantically-inappropriate type as
input. The type system can be made clearer with a few examples:

- Unrarefied and rarefied OTU tables are of the same _abstract_ type, and
methods will work with either, but some methods (e.g. alpha and beta diversity)
would semantically prefer a rarefied OTU table, while others (such as
rarefaction methods) expect an unrarified OTU table.

- Positionally-filtered alignments and unfiltered alignments are of the same
_abstract_ type, and both types can be passed to `make_phylogeny.py`. However,
generally the user would want to pass a positionally-filtered alignment, though
it may be necessary to use an unfiltered alignment in odd cases. The type system
would warn users when providing an unfiltered alignment, but the user could
override by acknowledging the warning.

- A pumpkin pie is functionally equivalent to an apple pie, but
may make less sense on the 4th of July. Pumpkin and apple pies are the same
_abstract_ type, but are different _concrete_ types. A warning would be issued
if a user tried to bring a pumpkin pie to a 4th of July party. An error would be
issued if a user tried to bring an alligator to the party.

The semantic type system will support a wide range of primitive and
microbial-ecology specific types, as well as arbitrary user-defined types.

### Plugin System
The plugin system will replace QIIME's current collection of scripts by
providing a repository of domain-specific computation (e.g., methods,
algorithms, and analyses commonly used in microbial ecology) that has been
registered with QIIME2.

The plugin system will support two types of computation: _methods_ and
_workflows_. A _method_ is an atomic unit of computation and is analogous to a
function: it takes some input(s) (some possibly required and some optional) and
produces some output(s). A _workflow_ is a directed acyclic graph (DAG) that
is composed of one or more _methods_ and/or other _workflows_. Conceptually, a
_workflow_ can still be viewed as a function that accepts input and creates
output, just like a _method_.

Each _method_/_workflow_ will be registered with QIIME2's plugin system. While
the way to register computation is an implementation detail, we propose the use
of Python 3's
[function annotations](http://legacy.python.org/dev/peps/pep-3107/) as a clean,
elegant, and built-in way to describe a function's inputs and outputs.
Alternative implementations include decorators or custom docstring formats.

When computation is registered with the plugin system, its inputs and outputs
will be described using types in the
[Semantic Type System](#Semantic Type System). Custom semantic types may also be
defined in the plugin system.

The plugins provided with QIIME2 will include functionality specific to
microbial ecology. The plugin system will be easily extendable to allow
users/developers to register their own custom functionality with the system.
Thus, there will be an "official" set of plugins that ship with QIIME2, but the
system will also allow users to install plugins from other sources. The plugin
system allows the QIIME2 ecosystem to grow without requiring all methods to be
specifically added to the QIIME2 distribution.

## Deliverables
Details will be filled in after discussion of the roadmap has taken place (so we
know what actually needs to be done).

## Timeline
Details will be filled in after discussion of the roadmap has taken place (so we
know what actually needs to be done).
