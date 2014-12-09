import skbio
from scipy.stats import pearsonr, spearmanr

from qiime.types.parameterized import ChooseOne, Range
from qiime.types.primitives import Decimal, String
from . import qiime
from .types import DistanceMatrix, OrdinationResults, SampleMetadata

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
