QIIME2
======

[![Build Status](https://travis-ci.org/biocore/metoo.png?branch=master)](https://travis-ci.org/biocore/metoo) [![Coverage Status](https://coveralls.io/repos/biocore/metoo/badge.png)](https://coveralls.io/r/biocore/metoo)

*Staging ground for QIIME 2 development*

This repository serves as a staging ground for the next major version of
[QIIME](http://qiime.org/) (i.e., QIIME2), which will be a complete redesign
and reimplementation of the package.

**Note:** This repository exists mainly for developers and is not intended for
production. It will be transitioned to the canonical QIIME repo
([biocore/qiime](https://github.com/biocore/qiime)) when the package is ready
to be released. This package is under active development and all functionality
should be treated as **pre-alpha**.

# Executive Summary


## Differences

### Client-Server Architecture
QIIME2 will use a client-server architecture allowing it to provide a graphical
interface (this will also enable multiple arbitrary interfaces e.g. CLI, iPad, BaseSpace).
This architecture is supported in a single host (e.g. a laptop or VirtualBox) and multi-host deployment (e.g. a cluster or EC2).
**All interactions** with QIIME2 will happen through a standardized protocol provided by the server (_qiime-server_).
The goal of the protocol is to reduce complexity and duplication in defining multiple interfaces. [How is this different from pyqi?](#How is this different from pyqi?)
Additionally it will allow remote execution over a network barrier which has been a difficulty in the past with pyqi.

### Workers
Once the _qiime-server_ has received a request via the protocol, it will launch a worker job
to preform the computation. The _qiime-server_ will provide status updates to clients through the protocol.
The worker job will record the results as an _artifact_ in a database.

### Database
**Note: This is not intended to be a substitute for the QIIME database project.**

The database represents a significant departure from the way QIIME currently handles
data (e.g. a directory).  Presently, data is continuously serialized and deserialized
at each step to and from the file-system. The resulting data is highly denormalized:
sample ids are duplicated throughout every file format used in QIIME. Because
QIIME fundamentally deals with samples at every step, they will become the basis
of structuring output in a normalized way. The database will store normalized data
as _artifacts_. These are pieces of data which are the counterpart to QIIME's
input and output files.

### Graphical Interface (Web-based)
One of the primary motivations for a web-based interface is both the ease of use
and portability. We propose that the web-interface not merely wrap a command line interface, but
instead provide a powerful and interactive workflow centered interaction model.
Currently it is very difficult to create custom workflows in QIIME (only a few developers are able to).
The main purpose of the interface is to allow users to easily create arbitrary workflows
by dragging and dropping methods together. They will be guided by a strong
semantic type system to prevent easily avoided errors such as passing
pre-split-libraries sequence data into OTU picking workflows.
Users will then be able to preview, export, download, visualize, and view the history of their data as it becomes available.
Additionally they may be able to query their results like a database (because it is one).

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
but different _concrete_ types may be considered equivalent as long as the user
is aware that they may be providing a semantically-inappropriate type as input.

The type system can be made clearer with a few examples. In the context of
microbial ecology:

- Unrarefied and rarefied OTU tables are of the same _abstract_ type, and
methods will work with either, but some methods (e.g. alpha and beta diversity)
would semantically prefer a rarefied OTU table, while others (such as
rarefaction methods) expect an unrarified OTU table.

- Filtered and unfiltered alignments are of the same _abstract_ type, and both
types can be passed to `make_phylogeny.py`. However, generally the user would
want to pass a filtered alignment, though it may be necessary to use an
unfiltered alignment in odd cases. The type system would warn users when
provided an unfiltered alignment, but the user can override by acknowledging
the warning.

As an analogy: a pumpkin pie is functionally equivalent to an apple pie, but
may make less sense on the 4th of July. Pumpkin and apple pies are the same
_abstract_ type, but are different _concrete_ types.

The semantic type system will support a wide range of primitive and
microbial-ecology specific types, as well as arbitrary user-defined types.

### Plugin System
The plugin system will replace the 

### How is the protocol different from pyqi?


## Deliverables


## Timeline


# tl;dr:
Don't worry, it will be amazing.
