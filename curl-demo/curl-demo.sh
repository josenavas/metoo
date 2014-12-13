# In this demo we'll perform beta diversity analyses as seen in the
# scikit-bio-cookbook recipe:
#     http://nbviewer.ipython.org/github/biocore/scikit-bio-cookbook/blob/master/Exploring%20microbial%20community%20diversity.ipynb
#
# Note: input files are taken from this recipe.
#
# Original publication:
#     http://www.ncbi.nlm.nih.gov/pubmed/19502440

# Create a new study to perform analyses within.
curl -w "\n" -X POST -F name="88 Soils" -F description="Analysis of bacterial communities in 88 soil samples taken from North and South America" http://localhost:8888/studies

# Upload a distance matrix and per-sample metadata as artifacts; this is the
# "seed" data that we'll analyze. Typically the seed data will be raw sequence
# data obtained from the sequencing center.
curl -w "\n" -X POST -F name="unifrac-dm" -F artifact_type=/system/plugins/qiime/types/DistanceMatrix -F file=@dm.txt http://localhost:8888/studies/1/artifacts
curl -w "\n" -X POST -F name="sample-metadata" -F artifact_type=/system/plugins/qiime/types/SampleMetadata -F file=@map.txt http://localhost:8888/studies/1/artifacts

# Submit a job to run PCoA on our distance matrix artifact, which produces a
# new artifact containing the ordination results.
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/pcoa -F input_dm=/studies/1/artifacts/1 http://localhost:8888/studies/1/jobs

# Submit a job to compute the correlation between pH and soil moisture deficit
# (both are columns in our per-sample metadata). This method doesn't produce
# any new artifacts and simply returns a correlation coefficient between -1 and
# +1 (non-artifact output).
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/envcorr -F input_sample_metadata=/studies/1/artifacts/2 -F input_column1=PH -F input_column2=SOIL_MOISTURE_DEFICIT http://localhost:8888/studies/1/jobs

# In the previous example we used the default correlation method (Pearson).
# Let's specify Spearman correlation instead.
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/envcorr -F input_sample_metadata=/studies/1/artifacts/2 -F input_column1=PH -F input_column2=SOIL_MOISTURE_DEFICIT -F input_method=spearman http://localhost:8888/studies/1/jobs

# Submit a job to compute a distance matrix from three environmental variables
# (pH, soil moisture deficit, and latitude).
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/dm_from_env -F input_sample_metadata=/studies/1/artifacts/2 -F input_column=PH http://localhost:8888/studies/1/jobs
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/dm_from_env -F input_sample_metadata=/studies/1/artifacts/2 -F input_column=SOIL_MOISTURE_DEFICIT http://localhost:8888/studies/1/jobs
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/dm_from_env -F input_sample_metadata=/studies/1/artifacts/2 -F input_column=LATITUDE http://localhost:8888/studies/1/jobs

# Run Mantel tests to compare our UniFrac distance matrix against the three
# environmental distance matrices we computed above.
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/mantel -F input_x=/studies/1/artifacts/1 -F input_y=/studies/1/artifacts/4 -F input_method=spearman -F input_strict=false http://localhost:8888/studies/1/jobs
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/mantel -F input_x=/studies/1/artifacts/1 -F input_y=/studies/1/artifacts/5 -F input_method=spearman -F input_strict=false http://localhost:8888/studies/1/jobs
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/mantel -F input_x=/studies/1/artifacts/1 -F input_y=/studies/1/artifacts/6 -F input_method=spearman -F input_strict=false http://localhost:8888/studies/1/jobs

# Run Mantel tests for all pairs of distance matrices.
curl -w "\n" -X POST -F method=/system/plugins/qiime/methods/pwmantel -F input_dms=/studies/1/artifacts/1 -F input_dms=/studies/1/artifacts/4 -F input_dms=/studies/1/artifacts/5 -F input_dms=/studies/1/artifacts/6 -F input_labels=UniFrac -F input_labels=pH -F input_labels="Soil moisture deficit" -F input_labels=Latitude -F input_method=spearman -F input_strict=false http://localhost:8888/studies/1/jobs
