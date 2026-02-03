from dataclasses import asdict
from datetime import datetime

import numpy as np
import pandas as pd

from omero_metrics.tools import load
from omero_metrics.tools.data_type import KKM_MAPPINGS
from omero_metrics.tools.serializers import serialize


def concatenate_images(images: list):
    list_images = []
    list_channels = []
    for mm_image in images:
        image = mm_image.array_data
        result = [image[:, :, :, :, i] for i in range(image.shape[4])]
        channels = [c.name for c in mm_image.channel_series.channels]
        list_images.extend(result)
        list_channels.extend(channels)
    return list_images, list_channels


## Image context loaders
def FieldIlluminationDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
    }
    im.context = serialize(context)


def PSFBeadsDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    mip_z = np.max(im.mm_image.array_data[0, ...], axis=0)
    bead_properties = load.load_table_mm_metrics(
        im.dataset_manager.mm_dataset.output["bead_properties"]
    )
    image_bead_properties = bead_properties.loc[
        bead_properties["image_id"] == im.omero_image.getId()
    ]
    # TODO: This is a hack. We just reproduce what microscope-metrics does to extract the min-distance
    min_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_lateral_distance_factor
        * 2
    )
    half_min_distance_px = min_distance_px // 2
    beads_array = np.zeros(
        (
            image_bead_properties.bead_id.max() + 1,
            im.mm_image.shape_z,
            min_distance_px + 1,
            min_distance_px + 1,
            im.mm_image.shape_c,
        )
    )
    for _, row in image_bead_properties.iterrows():
        y_left = int(row.center_y) - half_min_distance_px
        y_right = int(row.center_y) + half_min_distance_px + 1
        x_left = int(row.center_x) - half_min_distance_px
        x_right = int(row.center_x) + half_min_distance_px + 1
        bead_array = im.mm_image.array_data[
            0,  # time 0
            :,  # z-dimension
            max(0, y_left) : min(
                im.mm_image.array_data.shape[2], y_right
            ),  # y-dimension
            max(0, x_left) : min(
                im.mm_image.array_data.shape[3], x_right
            ),  # x-dimension
            :,  # channel
        ]
        if bead_array.shape == beads_array[row.bead_id].shape:
            beads_array[row.bead_id] = bead_array
        else:
            # The bead was close to the edge of the image, so we need to blow it to size
            y_padding = (
                abs(y_left) if y_left < 0 else 0,
                (
                    abs(y_right - im.mm_image.array_data.shape[2])
                    if y_right > im.mm_image.array_data.shape[2]
                    else 0
                ),
            )
            x_padding = (
                abs(x_left) if x_left < 0 else 0,
                (
                    abs(x_right - im.mm_image.array_data.shape[3])
                    if x_right > im.mm_image.array_data.shape[3]
                    else 0
                ),
            )
            beads_array[row.bead_id] = np.pad(
                bead_array, ((0, 0), y_padding, x_padding, (0, 0))
            )

    im.mm_image.array_data = None
    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "mip_z": mip_z,
        "beads_properties": image_bead_properties,
        "beads_array": beads_array,
    }
    im.context = serialize(context)


def PSFBeadsDataset_output_AveragePSF(im):
    im.mm_image = load.load_image(im.omero_image, load_array=False)
    im.context = {"message": "View of output average PSF not supported yet"}


## Dataset context loaders
def FieldIlluminationDataset(dm):
    dm.load_data(load_images=True, force_reload=True)
    list_images, list_channels = concatenate_images(
        dm.mm_dataset.input_data.field_illumination_images
    )
    context = {
        "mm_dataset": dm.mm_dataset,
        "image_data": list_images,
        "channel_names": list_channels,
        "kkm": dm.kkm,
    }
    dm.context = serialize(context)


def PSFBeadsDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    context = {
        "mm_dataset": dm.mm_dataset,
        "kkm": dm.kkm,
    }
    dm.context = serialize(context)


def EmptyMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    context = {
        "project_id": int(pm.omero_project.getId()),
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
    }
    pm.context = serialize(context)


def HarmonizedMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    dates = []
    min_date = None
    max_date = None
    channels = set()
    kkm_list = KKM_MAPPINGS.get(pm.mm_dataset_collection.dataset_class)
    collection_key_measurements_by_kkm = {kkm: [] for kkm in kkm_list}
    collection_key_measurements_by_dataset_id = {}
    for dataset in pm.mm_dataset_collection.dataset_collection:
        if not dataset.processed:
            # In principle, omero-metrics is generating and processing datasets in one go, so this should never happen
            raise ValueError(f"Dataset {dataset.name} is not processed")
        key_measurements_by_kkm = {
            kkm: [
                {
                    # TODO: We are removing here time from the date, but this might bite us back at some point
                    # We should consider keeping time in the date
                    "date": dataset.acquisition_datetime.split("T")[0],
                    "dataset_id": int(dataset.data_reference.omero_object_id),
                    **{
                        km.channel_name: km[kkm]
                        for km in dataset.output.key_measurements
                    },
                }
            ]
            for kkm in kkm_list
        }
        [
            collection_key_measurements_by_kkm[kkm].extend(
                key_measurements_by_kkm[kkm]
            )
            for kkm in kkm_list
        ]
        collection_key_measurements_by_dataset_id[
            int(dataset.data_reference.omero_object_id)
        ] = {
            "caption": f"{dataset.name} acquired on {dataset.acquisition_datetime}",
            "head": [kkm.replace("_", " ").title() for kkm in kkm_list],
            "body": [
                [km[kkm] for kkm in kkm_list]
                for km in dataset.output.key_measurements
            ],
        }
        channels = channels | {
            km.channel_name for km in dataset.output.key_measurements
        }
        dates.append(dataset.acquisition_datetime)
        min_date = (
            min(min_date, dataset.acquisition_datetime)
            if min_date
            else dataset.acquisition_datetime
        )
        max_date = (
            max(max_date, dataset.acquisition_datetime)
            if max_date
            else dataset.acquisition_datetime
        )
    context = {
        "project_id": int(pm.omero_project.getId()),
        "key_measurements_by_kkm": collection_key_measurements_by_kkm,
        "key_measurements_by_dataset_id": collection_key_measurements_by_dataset_id,
        "channels": list(channels),
        "dates": dates,
        "min_date": min_date,
        "max_date": max_date,
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
        "kkm": kkm_list,
    }
    pm.context = serialize(context)
