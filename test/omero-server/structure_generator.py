# This script is used to geenrate a structure, as defined by the server_structure.yaml file in the same directory
# on the OMERO server. This structure is used to test the omero-metrics package.

import logging
import yaml
from hypothesis import given
from hypothesis import strategies as st
import numpy as np

from microscopemetrics.strategies import strategies as mm_st

logger = logging.getLogger(__name__)

BIT_DEPTH_TO_DTYPE = {
    8: np.uint8,
    16: np.uint16,
    32: np.float32,
}

def field_illumination_generator(args):
    @given(mm_st.st_field_illumination_test_data(
        nr_images=st.integers(
            min_value=args["nr_images"]["min"],
            max_value=args["nr_images"]["max"]),
        y_image_shape=st.integers(
            min_value=args["y_image_shape"]["min"],
            max_value=args["y_image_shape"]["max"]),
        x_image_shape=st.integers(
            min_value=args["x_image_shape"]["min"],
            max_value=args["x_image_shape"]["max"]),
        c_image_shape=st.integers(
            min_value=args["c_image_shape"]["min"],
            max_value=args["c_image_shape"]["max"]),
        dtype=st.just(BIT_DEPTH_TO_DTYPE[args["bit_depth"]]),
        signal=st.integers(
            min_value=args["signal"]["min"],
            max_value=args["signal"]["max"]),
        target_min_intensity=st.floats(
            min_value=args["target_min_intensity"]["min"],
            max_value=args["target_min_intensity"]["max"]),
        target_max_intensity=st.floats(
            min_value=args["target_max_intensity"]["min"],
            max_value=args["target_max_intensity"]["max"]),
        center_y_relative=st.floats(
            min_value=args["center_y_relative"]["min"],
            max_value=args["center_y_relative"]["max"]),
        center_x_relative=st.floats(
            min_value=args["center_x_relative"]["min"],
            max_value=args["center_x_relative"]["max"]),
        dispersion=st.floats(
            min_value=args["dispersion"]["min"],
            max_value=args["dispersion"]["max"]),
    ))
    def gen_dataset(strategie):
        return strategie["images"]

    datasets = {}

    for i in range(args["nr_datasets"]):
        datasets[f"{args['name_dataset']}_nr{i}"] = gen_dataset()

    pass
    return datasets

GENERATOR_MAPPER = {
    "field_illumination_generator": field_illumination_generator,
}

with open("server_structure.yaml", "r") as f:
    server_structure = yaml.load(f, Loader=yaml.SafeLoader)

for microscope in server_structure["microscopes"].values():
    for project in microscope["projects"].values():
        GENERATOR_MAPPER[project["generator"]](project)



# mm_st.st_field_illumination_test_data