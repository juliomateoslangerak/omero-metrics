import logging

import numpy as np
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper, ProjectWrapper, FileAnnotationWrapper
import microscopemetrics_schema.datamodel as mm_schema
from linkml_runtime.loaders import yaml_loader

from omero_metrics.tools import omero_tools

# Creating logging services
logger = logging.getLogger(__name__)

DATASET_TYPES = ["FieldIlluminationDataset", "PSFBeadsDataset"]

def load_project(conn: BlitzGateway, project_id: int) -> mm_schema.MetricsDatasetCollection:
    collection = mm_schema.MetricsDatasetCollection()
    file_anns = []
    dataset_types = []
    project = conn.getObject("Project", project_id)
    for file_ann in project.listAnnotations():
        if isinstance(file_ann, FileAnnotationWrapper):
            ds_type = file_ann.getFileName().split("_")[0]
            if ds_type in DATASET_TYPES:
                file_anns.append(file_ann)
                dataset_types.append(ds_type)

    for file_ann, ds_type in zip(file_anns, dataset_types):
        collection.datasets.append(
            yaml_loader.loads(file_ann.getFileInChunks().__next__().decode(), target_class=getattr(mm_schema, ds_type))
        )

    return collection


def load_mm_dataset(conn: BlitzGateway, dataset_id: int) -> mm_schema.MetricsDataset:
    pass


def load_image(image: ImageWrapper) -> np.ndarray:
    """Load an image from OMERO and return it as a numpy array in the order desired by the analysis"""
    # OMERO order zctyx -> microscope-metrics order TZYXC
    return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))


