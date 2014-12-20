import skbio
import skbio.diversity.beta
import numpy as np
from scipy.stats import pearsonr, spearmanr

from framework.types.parameterized import ChooseOne, List, Range
from framework.types.primitives import Boolean, Decimal, Integer, String
from . import qiime
from .types import (
    DistanceMatrix, OrdinationResults, SampleMetadata, PairwiseMantelResults,
    BioenvResults)

@qiime.register_method("Principal Coordinates Analysis (PCoA)")
def pcoa(dm: DistanceMatrix) -> OrdinationResults:
    """Perform Principal Coordinates Analysis (PCoA) on a distance matrix."""
    return skbio.stats.ordination.PCoA(dm).scores()

@qiime.register_method("Environmental variable correlation")
def envcorr(sample_metadata: SampleMetadata, column1: String, column2: String,
            method: ChooseOne(String, ['pearson', 'spearman']) = 'pearson') -> Range(Decimal, -1, 1):
    """Compute correlation between two numeric environmental variables."""
    if method == 'pearson':
        corr_function = pearsonr
    elif method == 'spearman':
        corr_function = spearmanr
    else:
        # shouldn't be possible to get here
        pass
    return corr_function(sample_metadata[column1], sample_metadata[column2])[0]

@qiime.register_method("Distance matrix from environmental variable")
def dm_from_env(sample_metadata: SampleMetadata, column: String) -> DistanceMatrix:
    """Compute a distance matrix from a numeric environmental variable."""
    return skbio.diversity.beta.pw_distances(
        sample_metadata[column].values[:, np.newaxis],
        ids=sample_metadata.index, metric='euclidean')

# TODO add `lookup` support
@qiime.register_method("Mantel test")
def mantel(x: DistanceMatrix, y: DistanceMatrix,
           method: ChooseOne(String, ['pearson', 'spearman']) = 'pearson',
           permutations: Range(Integer, 0, None) = 999,
           alternative: ChooseOne(String, ['two-sided', 'greater', 'less']) = 'two-sided',
           strict: Boolean = True) -> (Range(Decimal, -1, 1),
                                       Range(Decimal, 0, 1),
                                       Range(Integer, 0, None)): # TODO return named tuples
    """Compute correlation between distance matrices using the Mantel test."""
    return skbio.stats.distance.mantel(
        x, y, method=method, permutations=permutations,
        alternative=alternative, strict=strict)

# TODO add `lookup` support
@qiime.register_method("Pairwise Mantel test")
def pwmantel(dms: List(DistanceMatrix), labels: List(String) = (),
             method: ChooseOne(String, ['pearson', 'spearman']) = 'pearson',
             permutations: Range(Integer, 0, None) = 999,
             alternative: ChooseOne(String, ['two-sided', 'greater', 'less']) = 'two-sided',
             strict: Boolean = True) -> PairwiseMantelResults:
    """Run Mantel tests for every pair of distance matrices."""
    # scikit-bio expects None for default case
    labels = None if labels == () else labels

    return skbio.stats.distance.pwmantel(
        dms, labels=labels, method=method, permutations=permutations,
        alternative=alternative, strict=strict)

@qiime.register_method("BIO-ENV")
def bioenv(distance_matrix: DistanceMatrix, sample_metadata: SampleMetadata,
           columns: List(String) = ()) -> BioenvResults:
    """Find subset of variables maximally correlated with distances."""
    # scikit-bio expects None for default case
    columns = None if columns == () else columns

    return skbio.stats.distance.bioenv(distance_matrix, sample_metadata,
                                       columns=columns)
