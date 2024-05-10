import logging
from microscopemetrics_schema.datamodel.microscopemetrics_schema import (
    FieldIlluminationDataset,
)
import numpy as np
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper, ProjectWrapper, FileAnnotationWrapper
import microscopemetrics_schema.datamodel as mm_schema
from linkml_runtime.loaders import yaml_loader
import pandas as pd
from omero_metrics.tools import omero_tools
from .data_preperation import get_table_originalFile_id

# Creating logging services
logger = logging.getLogger(__name__)

DATASET_TYPES = ["FieldIlluminationDataset", "PSFBeadsDataset"]


def load_project(conn: BlitzGateway, project_id: int) -> mm_schema.MetricsDatasetCollection:
    collection = mm_schema.MetricsDatasetCollection()
    file_anns = []
    dataset_types = []
    project = conn.getObject("Project", project_id)
    try:
        for file_ann in project.listAnnotations():
            if isinstance(file_ann, FileAnnotationWrapper):
                ds_type = file_ann.getFileName().split("_")[0]
                if ds_type in DATASET_TYPES:
                    file_anns.append(file_ann)
                    dataset_types.append(ds_type)

        for file_ann, ds_type in zip(file_anns, dataset_types):
            collection.datasets.append(
                yaml_loader.loads(file_ann.getFileInChunks().__next__().decode(),
                                  target_class=getattr(mm_schema, ds_type))
            )
        return collection
    except Exception as e:
        logger.error(f"Error loading project {project_id}: {e}")
        return collection


def load_mm_dataset(conn: BlitzGateway, dataset_id: int) -> mm_schema.MetricsDataset:
    pass


def load_image(image: ImageWrapper) -> np.ndarray:
    """Load an image from OMERO and return it as a numpy array in the order desired by the analysis"""
    # OMERO order zctyx -> microscope-metrics order TZYXC
    return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))


def load_dataset_data(conn: BlitzGateway, dataset: DatasetWrapper) -> mm_schema.MetricsDataset:
    pass


def get_project_data(collections: mm_schema.MetricsDatasetCollection) -> pd.DataFrame:
    data = []
    for dataset in collections.datasets:
        data.append([dataset.__class__.__name__, dataset.data_reference.omero_object_type,
                     dataset.data_reference.omero_object_id, dataset.processed, dataset.acquisition_datetime])
    df = pd.DataFrame(data, columns=["Analysis_type", "Omero_object_type", "Omero_object_id", "Processed",
                                     "Acquisition_datetime"])
    return df


def get_dataset_by_id(collections: mm_schema.MetricsDatasetCollection, dataset_id) -> mm_schema.MetricsDataset:
    try:
        dataset = [i for i in collections.datasets if i.data_reference.omero_object_id == dataset_id][0]
        return dataset
    except:
        return None


def get_images_intensity_profiles(dataset: mm_schema.MetricsDataset) -> pd.DataFrame:
    data = []
    for i, j in zip(dataset.input['field_illumination_image'], dataset.output["intensity_profiles"]):
        data.append([i['data_reference']['omero_object_id'], j['data_reference']['omero_object_id'], i['shape_c']])
    df = pd.DataFrame(data, columns=["Field_illumination_image", "Intensity_profiles", "Channel"])
    return df


def get_key_values(var: FieldIlluminationDataset.output) -> pd.DataFrame:
    data_dict = var.key_values.__dict__
    data_dict = [value + [key] for key, value in data_dict.items() if
                 isinstance(value, list) and key not in ['name', 'description', 'data_reference', 'linked_references',
                                                         'channel_name']]
    df = pd.DataFrame(data_dict, columns=var.key_values.channel_name + ['Parameter'])
    return df


def concatenate_images(conn, df):
    image_0 = conn.getObject('Image', df['Field_illumination_image'][0])
    image_array_0 = load_image(image_0)
    result = image_array_0
    for i in range(1, len(df)):
        image = conn.getObject('Image', df['Field_illumination_image'][i])
        image_array = load_image(image)
        result = np.concatenate((result, image_array), axis=-1)
    return result


def get_all_intensity_profiles(conn, data_df):
    df_01 = pd.DataFrame()
    for i, row in data_df.iterrows():
        file_id = conn.getObject('FileAnnotation', row.Intensity_profiles).getFile().getId()
        data = get_table_originalFile_id(conn, str(file_id))
        for j in range(row.Channel):
            regx_find = f'ch0{j}'
            ch = i + j
            regx_repl = f'Ch0{ch}'
            data.columns = data.columns.str.replace(regx_find, regx_repl)
        df_01 = pd.concat([df_01, data], axis=1)
    return df_01
