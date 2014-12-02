from io import StringIO

import skbio

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
