from dataclasses import asdict

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
    collection_df = pd.DataFrame()
    for dataset in pm.mm_dataset_collection.dataset_collection:
        if not dataset.processed:
            # In principle, omero-metrics is generating and processing datasets in one go, so this should never happen
            raise ValueError(f"Dataset {dataset.name} is not processed")
        dataset_df = pd.DataFrame.from_records(
            [asdict(km) for km in dataset.output.key_measurements]
        )
        dataset_df["acquisition_datetime"] = dataset.acquisition_datetime
        collection_df = pd.concat([collection_df, dataset_df])
    context = {
        "project_id": int(pm.omero_project.getId()),
        "key_measurements_df": collection_df,
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
        "kkm": KKM_MAPPINGS.get(pm.mm_dataset_collection.dataset_class),
    }
    pm.context = serialize(context)
