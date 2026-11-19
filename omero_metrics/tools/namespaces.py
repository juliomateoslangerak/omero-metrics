import microscopemetrics_schema.datamodel as mm_schema

# NameSpaces to use in OMERO
NS_OMERO_METRICS_PREFIX = "omero-metrics:"
NS_LAST_KEY_KEY_MEASUREMENT = f"{NS_OMERO_METRICS_PREFIX}last-key-key-measurement"
NS_ANALYSIS_RUN_METADATA = f"{NS_OMERO_METRICS_PREFIX}analysis-run-metadata"
NS_COMMENT = f"{NS_OMERO_METRICS_PREFIX}comment"
NS_THRESHOLDS = f"{NS_OMERO_METRICS_PREFIX}thresholds"
# Re-applicable Chromagnon correction file (.chromagnon.csv/.tif) attached to a
# dataset by the chromatic shift analysis. Not an assay namespace, so it is not
# read as the dataset YAML.
NS_CHROMAGNON_CORRECTION = f"{NS_OMERO_METRICS_PREFIX}chromagnon-correction"

LIST_NS_MICROSCOPEMETRICS_SCHEMA_INPUT_PARAMETERS = [
    f"{NS_OMERO_METRICS_PREFIX}{cls.class_class_curie}"
    for cls in mm_schema.MetricsInputParameters.__subclasses__()
]

LIST_NS_MICROSCOPEMETRICS_SCHEMA_SAMPLES = [
    f"{NS_OMERO_METRICS_PREFIX}{cls.class_class_curie}"
    for cls in mm_schema.Sample.__subclasses__()
]

LIST_NS_MICROSCOPEMETRICS_SCHEMA_ASSAYS = [
    f"{NS_OMERO_METRICS_PREFIX}{cls.class_class_curie}"
    for cls in mm_schema.MetricsDataset.__subclasses__()
]
