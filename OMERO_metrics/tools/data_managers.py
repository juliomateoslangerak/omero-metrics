import datetime
import logging
from typing import Union
from microscopemetrics.samples import field_illumination, psf_beads
from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema)
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper
from . import load, dump, update, delete

logger = logging.getLogger(__name__)
DATA_TYPE_MAPPINGS = {"Dataset": 0, "Image": 1}
ANALYSIS_MAPPINGS = {
    "analise_field_illumination":
        field_illumination.analise_field_illumination,
    "analyse_psf_beads":
        psf_beads.analyse_psf_beads,
}
SAMPLE_MAPPINGS = {
    "FieldIllumination": field_illumination,
    "PSFBeads": psf_beads,
}
DATASET_MAPPINGS = {
    "FieldIlluminationDataset":
        mm_schema.FieldIlluminationDataset,
    "PSFBeadsDataset":
        mm_schema.PSFBeadsDataset,
}
INPUT_MAPPINGS = {
    "FieldIlluminationInput":
        mm_schema.FieldIlluminationInput,
    "PSFBeadsInput":
        mm_schema.PSFBeadsInput,
}
OBJECT_TO_DUMP_FUNCTION = {
    mm_schema.Image: dump.dump_image,
    mm_schema.Roi: dump.dump_roi,
    mm_schema.Tag: dump.dump_tag,
    mm_schema.KeyValues: dump.dump_key_value,
    mm_schema.Table: dump.dump_table,
}
TEMPLATE_MAPPINGS = {
    "FieldIlluminationDataset": [
        "OMERO_metrics/omero_views/center_view_dataset_foi.html",
        "OMERO_metrics/omero_views/center_view_image.html",
    ],
    "PSFBeadsDataset": [
        "OMERO_metrics/omero_views/center_view_dataset_psf_beads.html",
        "OMERO_metrics/omero_views/center_view_image_psf.html",
    ],
    "unknown_analysis":
        "OMERO_metrics/omero_views/center_view_unknown_analysis_type.html",
    "unprocessed_analysis":
        "OMERO_metrics/omero_views/unprocessed_dataset.html",
}
