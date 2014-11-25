from io import StringIO

import skbio

from qiime.types import Artifact
from . import qiime

@qiime.register_type("distance matrix")
class DistanceMatrix(Artifact):
    """Symmetric, hollow 2-D matrix of distances."""
    data_type = skbio.DistanceMatrix

    @classmethod
    def from_blob(cls, blob):
        return cls.data_type.read(StringIO(blob.decode('utf-8')))

    @classmethod
    def to_blob(cls, data):
        blob = StringIO()
        data.write(blob)
        return blob.getvalue()

@qiime.register_type("UniFrac distance matrix")
class UniFracDistanceMatrix(DistanceMatrix):
    """..."""
    pass

@qiime.register_type("bray-curtis distance matrix")
class BrayCurtisDistanceMatrix(DistanceMatrix):
    """---"""
    pass

@qiime.register_type("contingency table")
class ContingencyTable(Artifact):
    """2-D table of observation counts within each sample."""
    pass

@qiime.register_type("otu table")
class OTUTable(ContingencyTable):
    """OTU table"""
    pass

# TODO this hierarchy probably isn't the best way to handle this, but useful
# for testing multiple inheritance

@qiime.register_type("rarefied table")
class RarefiedTable(Artifact):
    """Rarefied table"""
    pass

@qiime.register_type("rarefied otu table")
class RarefiedOTUTable(OTUTable, RarefiedTable):
    """Rarefied OTU table"""
    pass

@qiime.register_method("Add distance matrices")
def add_dms(a: DistanceMatrix, b: DistanceMatrix) -> DistanceMatrix:
    """Add two distance matrices of the same shape."""
    if a.shape != b.shape:
        raise ValueError("Distance matrices must be the same shape in order to add them.")
    return skbio.DistanceMatrix(a.data + b.data)

@qiime.register_method("other method")
def something_else(a: int, b: str) -> dict:
    pass

# @qiime.register_workflow("some workflow")
# def some_workflow(Step,
#                   dm: DistanceMatrix,
#                   other: OtherThing,
#                   param1: Integer=3) -> (Something, SomethingElse):
#     """Description of workflow
#
#     """
#     a = Step('org.qiime.plugins.qiime.methods.some_method', dm, name=param1)
#     b = Step('org.qiime.plugins.qiime.methods.something_else', other, p2=2)
#     c = Step('org.qiime.plugins.qiime.methods.final_step', a[0], b[0])
# 
#     return a[1], c[0]
#
# @qiime.register_parallel("some parallel")
# def some_parallel(Map, Apply, Reduce):
#     """something"""
#     @Map
#     def some_map(a: Something, processes: Integer=1) -> Yields(SomethingElse):
#         pass
#
#     @Apply
#     def some_apply(a: SomethingElse) -> AnotherThing:
#         pass
#
#     @Reduce
#     def some_reduce(a: Yields(AnotherThing)) -> Result
#         pass
#
#
#
# {
#     name: "my work",
#     artifacts: ['arfifact1', 'artifact2']
#     parameters: {}
#     method: "plugins.qiime.methods.do_thing"
# }
