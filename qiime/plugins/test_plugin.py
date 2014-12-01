from io import StringIO

import skbio

from qiime.types.parameterized import ChooseMany, List
from qiime.types.primitives import Integer, Decimal

from qiime.types import Artifact
from . import qiime

@qiime.register_type
class DistanceMatrix(Artifact):
    """Symmetric, hollow 2-D matrix of distances."""
    name = 'distance matrix'
    data_type = skbio.DistanceMatrix

    @classmethod
    def load(cls, blob):
        return cls.data_type.read(StringIO(blob.decode('utf-8')))

    @classmethod
    def save(cls, data):
        blob = StringIO()
        data.write(blob)
        return blob.getvalue()

@qiime.register_type
class UniFracDistanceMatrix(DistanceMatrix):
    """..."""
    name = "UniFrac distance matrix"

@qiime.register_type
class BrayCurtisDistanceMatrix(DistanceMatrix):
    """---"""
    name = "bray-curtis distance matrix"

@qiime.register_type
class ContingencyTable(Artifact):
    """2-D table of observation counts within each sample."""
    name = "contingency table"

@qiime.register_type
class OTUTable(ContingencyTable):
    """OTU table"""
    name = "OTU table"

# TODO this hierarchy probably isn't the best way to handle this, but useful
# for testing multiple inheritance

@qiime.register_type
class RarefiedTable(Artifact):
    """Rarefied table"""
    name = "rarefied table"

@qiime.register_type
class RarefiedOTUTable(OTUTable, RarefiedTable):
    """Rarefied OTU table"""
    name = "rarefied OTU table"

@qiime.register_method("Add distance matrices")
def add_dms(a: DistanceMatrix,
            c: ChooseMany(Integer, [10, 42, 100]),
            b: DistanceMatrix='/studies/1/artifacts/2'
            ) -> (DistanceMatrix, ChooseMany(Integer, [1, 2, 3, 42]), Decimal):
    """Add two distance matrices of the same shape."""
    if a.shape != b.shape:
        raise ValueError("Distance matrices must be the same shape in order to add them.")
    print(c)
    print(type(c))
    return skbio.DistanceMatrix(a.data + b.data), [1, 2, 3], 4.1


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
