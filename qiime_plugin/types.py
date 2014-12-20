from io import StringIO

import pandas as pd
import skbio

from framework.types import Artifact
from . import qiime

# TODO make this consistent with method registration
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
    """Distance matrix containing UniFrac distances."""
    name = "UniFrac distance matrix"

@qiime.register_type
class BrayCurtisDistanceMatrix(DistanceMatrix):
    """Distance matrix containing Bray-Curtis distances."""
    name = "bray-curtis distance matrix"

@qiime.register_type
class SampleMetadata(Artifact):
    """Metadata on a per-sample basis."""
    name = 'sample metadata'
    data_type = pd.DataFrame

    @classmethod
    def load(cls, blob):
        return pd.read_csv(StringIO(blob.decode('utf-8')), sep='\t',
                           index_col=0)

    @classmethod
    def save(cls, data):
        blob = StringIO()
        data.to_csv(blob, sep='\t')
        return blob.getvalue()

@qiime.register_type
class OrdinationResults(Artifact):
    """Results from applying an ordination technique to a distance matrix."""
    name = 'ordination results'
    data_type = skbio.stats.ordination.OrdinationResults

    @classmethod
    def load(cls, blob):
        return cls.data_type.read(StringIO(blob.decode('utf-8')))

    @classmethod
    def save(cls, data):
        blob = StringIO()
        data.write(blob)
        return blob.getvalue()

# TODO add intermediate base class for table-like stats results (e.g.,
# StatsResults)

@qiime.register_type
class PairwiseMantelResults(Artifact):
    """Results from performing pairwise Mantel tests on distance matrices."""
    name = 'pairwise Mantel results'
    data_type = pd.DataFrame

    @classmethod
    def load(cls, blob):
        # TODO make sure this works with MultiIndex
        return pd.read_csv(StringIO(blob.decode('utf-8')), sep='\t',
                           index_col=0)

    @classmethod
    def save(cls, data):
        blob = StringIO()
        data.to_csv(blob, sep='\t')
        return blob.getvalue()

@qiime.register_type
class BioenvResults(Artifact):
    """Results from performing bioenv test."""
    name = 'BIO-ENV results'
    data_type = pd.DataFrame

    @classmethod
    def load(cls, blob):
        return pd.read_csv(StringIO(blob.decode('utf-8')), sep='\t',
                           index_col=0)

    @classmethod
    def save(cls, data):
        blob = StringIO()
        data.to_csv(blob, sep='\t')
        return blob.getvalue()
