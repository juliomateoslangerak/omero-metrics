# This script is used to geenrate a structure, as defined by the server_structure.yaml file in the same directory
# on the OMERO server. This structure is used to test the omero-metrics package.

import logging
import yaml
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
import numpy as np
import random

from microscopemetrics.strategies.strategies import _gen_field_illumination_image
from microscopemetrics.samples import numpy_to_mm_image
from microscopemetrics_schema import datamodel as mm_schema

logger = logging.getLogger(__name__)

BIT_DEPTH_TO_DTYPE = {
    8: np.uint8,
    16: np.uint16,
    32: np.float32,
}


from datetime import datetime, timedelta

def generate_monthly_dates(start_date, nr_months, month_frequency=1):
    dates = []
    current_date = start_date
    for _ in range(nr_months):
        month = current_date.month - 1 + 1
        year = current_date.year + month // 12
        month = month % 12 + month_frequency
        day = min(current_date.day, [31,
            29 if year%4==0 and (year%100!=0 or year%400==0) else 28,
            31,30,31,30,31,31,30,31,30,31][month-1])
        date1 = datetime(year, month, day)
        dates.append(date1.strftime("%Y-%m-%d"))
        current_date = date1
    return dates


def field_illumination_generator(args, microscope_name):
    datasets = []
    dates = generate_monthly_dates(args["start_date"], args["nr_datasets"], args["month_frequency"])

    for dataset_id in range(args["nr_datasets"]):
        print(f"Generating dataset {dataset_id} for {args['name_dataset']}")
        datasets.append(
            mm_schema.FieldIlluminationDataset(
                name=f"{args['name_dataset']}_{dates[dataset_id]}",
                description=args["description_dataset"],
                acquisition_datetime=dates[dataset_id],
                microscope=mm_schema.Microscope(name=microscope_name),
                input=mm_schema.FieldIlluminationInput(
                    field_illumination_image=[
                        numpy_to_mm_image(
                            array=_gen_field_illumination_image(
                                y_shape=random.randint(args["y_image_shape"]["min"], args["y_image_shape"]["max"]),
                                x_shape=random.randint(args["x_image_shape"]["min"], args["x_image_shape"]["max"]),
                                c_shape=len(channel_names),
                                y_center_rel_offset=[random.uniform(args["center_y_relative"]["min"], args["center_y_relative"]["max"]) for _ in range(len(channel_names))],
                                x_center_rel_offset=[random.uniform(args["center_x_relative"]["min"], args["center_x_relative"]["max"]) for _ in range(len(channel_names))],
                                dispersion=[random.uniform(args["dispersion"]["min"], args["dispersion"]["max"]) for _ in range(len(channel_names))],
                                target_min_intensity=[random.uniform(args["target_min_intensity"]["min"], args["target_min_intensity"]["max"]) for _ in range(len(channel_names))],
                                target_max_intensity=[random.uniform(args["target_max_intensity"]["min"], args["target_max_intensity"]["max"]) for _ in range(len(channel_names))],
                                do_noise=True,
                                signal=[random.randint(args["signal"]["min"], args["signal"]["max"]) for _ in range(len(channel_names))],
                                dtype=BIT_DEPTH_TO_DTYPE[args["bit_depth"]],
                            ),
                            name=f"{args['name_dataset']}_{'_'.join(channel_names)}_{dates[dataset_id]}",
                            description=f"An image taken on the {microscope_name} microscope on the {dates[dataset_id]} for QC",
                            channel_names=args["channel_names"][image_id],
                        )
                        for image_id, channel_names in enumerate(args["channel_names"])
                    ]
                )
            )
        )

    return datasets


GENERATOR_MAPPER = {
    "FieldIlluminationDataset": field_illumination_generator,
}

if __name__ == "__main__":
    with open("server_structure.yaml", "r") as f:
        server_structure = yaml.load(f, Loader=yaml.SafeLoader)

    projects = []
    for microscope in server_structure["microscopes"].values():
        for project in microscope["projects"].values():
            projects[] = mm_schema.HarmonizedMetricsDatasetCollection(
                name=project["name_project"],
                description=project["description_project"],
                datasets=GENERATOR_MAPPER[project["analysis_class"]](project, microscope["name"]),
                dataset_class=project["analysis_class"],
            )

    pass

