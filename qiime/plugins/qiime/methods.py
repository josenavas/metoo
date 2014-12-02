import skbio

from qiime.types.parameterized import ChooseMany, List
from qiime.types.primitives import Integer, Decimal
from . import qiime
from .types import DistanceMatrix

@qiime.register_method("Add distance matrices")
def add_dms(a: DistanceMatrix,
            c: ChooseMany(Integer, [10, 42, 100]),
            b: DistanceMatrix='/studies/1/artifacts/2'
            ) -> (DistanceMatrix, ChooseMany(Integer, [1, 2, 3, 42]), List(List(Decimal))):
    """Add two distance matrices of the same shape."""
    if a.shape != b.shape:
        raise ValueError("Distance matrices must be the same shape in order to add them.")
    print(c)
    print(type(c))
    return skbio.DistanceMatrix(a.data + b.data), [1, 2, 3], [[4.1], [2.2]]
