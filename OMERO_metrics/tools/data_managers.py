import datetime
import logging
from typing import Union
import microscopemetrics_schema.datamodel.microscopemetrics_schema as mm_schema
from microscopemetrics.samples import field_illumination, psf_beads
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper
from . import delete, dump, load, update

logger = logging.getLogger(__name__)
DATA_TYPE_MAPPINGS = {"Dataset": 0, "Image": 1}
ANALYSIS_MAPPINGS = {
    "analise_field_illumination": field_illumination.analise_field_illumination,
    "analyse_psf_beads": psf_beads.analyse_psf_beads,
}
