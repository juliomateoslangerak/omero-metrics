import logging

import numpy as np
from omero.gateway import DatasetWrapper, ImageWrapper, ProjectWrapper

import omero_tools

# Creating logging services
logger = logging.getLogger(__name__)


def load_image(image: ImageWrapper) -> np.ndarray:
    """Load an image from OMERO and return it as a numpy array in the order desired by the analysis"""
    # OMERO order zctyx -> microscope-metrics order TZYXC
    return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))


def load_dataset(dataset):
    pass


def load_project(project):
    pass
