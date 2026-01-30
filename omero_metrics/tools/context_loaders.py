from dataclasses import asdict
from datetime import datetime

import pandas as pd

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


def context_loader_FieldIlluminationDataset(dm):
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


def context_loader_PSFBeadsDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    context = {
        "mm_dataset": dm.mm_dataset,
        "kkm": dm.kkm,
    }
    dm.context = serialize(context)


def context_loader_EmptyMetricsDatasetCollection(pm):
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


def context_loader_HarmonizedMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    dates = []
    min_date = None
    max_date = None
    channels = set()
    kkm_list = KKM_MAPPINGS.get(pm.mm_dataset_collection.dataset_class)
    collection_key_measurements = {kkm: [] for kkm in kkm_list}
    for dataset in pm.mm_dataset_collection.dataset_collection:
        if not dataset.processed:
            # In principle, omero-metrics is generating and processing datasets in one go, so this should never happen
            raise ValueError(f"Dataset {dataset.name} is not processed")
        key_measurements = {
            kkm: [
                {
                    "date": dataset.acquisition_datetime.split("T")[0],
                    **{
                        km.channel_name: km[kkm]
                        for km in dataset.output.key_measurements
                    },
                }
            ]
            for kkm in kkm_list
        }
        channels = channels | {
            km.channel_name for km in dataset.output.key_measurements
        }
        [
            collection_key_measurements[kkm].extend(key_measurements[kkm])
            for kkm in kkm_list
        ]
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
        "key_measurements": collection_key_measurements,
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
