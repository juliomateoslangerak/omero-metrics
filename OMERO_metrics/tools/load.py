import logging
from microscopemetrics_schema.datamodel.microscopemetrics_schema import (
    FieldIlluminationDataset,
    PSFBeadsDataset,
)
import yaml
import numpy as np
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
    FileAnnotationWrapper,
    MapAnnotationWrapper,
)
import microscopemetrics_schema.datamodel as mm_schema
from linkml_runtime.loaders import yaml_loader
import pandas as pd
from OMERO_metrics.tools import omero_tools
from OMERO_metrics.tools.data_preperation import (
    get_table_original_file_id,
)

# Creating logging services
logger = logging.getLogger(__name__)
import collections
import omero
from datetime import datetime


DATASET_TYPES = ["FieldIlluminationDataset", "PSFBeadsDataset"]

INPUT_IMAGES_MAPPING = {
    "FieldIlluminationDataset": "field_illumination_image",
    "PSFBeadsDataset": "psf_beads_images",
}

OUTPUT_DATA = {
    "FieldIlluminationDataset": "intensity_profiles",
    "PSFBeadsDataset": "psf_beads",
}

DATASET_IMAGES = {
    "FieldIlluminationDataset": {
        "input_data": ["field_illumination_image"],
        "output": [],
    },
    "PSFBeadsDataset": {
        "input_data": ["psf_beads_images"],
        "output": ["average_bead"],
    },
}


def get_annotations_tables(conn, group_id):
    all_annotations = conn.getObjects("Annotation", opts={"group": group_id})
    file_ann_cols = [
        "Name",
        "ID",
        "File_ID",
        "Description",
        "Date",
        "Owner",
        "NS",
        "Mimetype",
    ]
    file_ann_rows = []
    map_ann_cols = ["Name", "ID", "Description", "Date", "Owner", "NS"]
    map_ann_rows = []
    for ann in all_annotations:
        if ann.getNs() and ann.getNs().startswith("microscopemetrics"):
            if isinstance(ann, FileAnnotationWrapper):
                file_ann_rows.append(
                    [
                        ann.getFile().getName(),
                        ann.getId(),
                        ann.getFile().getId(),
                        ann.getDescription(),
                        ann.getDate(),
                        ann.getOwner().getName(),
                        ann.getNs(),
                        ann.getFile().getMimetype(),
                    ]
                )
            elif isinstance(ann, omero.gateway.MapAnnotationWrapper):
                map_ann_rows.append(
                    [
                        ann.getName(),
                        ann.getId(),
                        ann.getDescription(),
                        ann.getDate(),
                        ann.getOwner().getName(),
                        ann.getNs(),
                    ]
                )
    file_ann_df = pd.DataFrame(file_ann_rows, columns=file_ann_cols)
    map_ann_df = pd.DataFrame(map_ann_rows, columns=map_ann_cols)
    file_ann_df["Date"] = pd.to_datetime(file_ann_df["Date"])
    map_ann_df["Date"] = pd.to_datetime(map_ann_df["Date"])
    return file_ann_df, map_ann_df


def get_annotations_list_group(conn, group_id):
    projects = conn.getObjects("Project", opts={"group": group_id})
    data = []
    columns = [
        "Name",
        "ID",
        "File_ID",
        "Description",
        "Date",
        "Owner",
        "Project_ID",
        "Project_Name",
        "NS",
        "Type",
    ]
    for p in projects:
        for ds in p.listAnnotations():
            data.append(
                [
                    ds.getFile().getName(),
                    ds.getId(),
                    ds.getFile().getId(),
                    ds.getDescription(),
                    ds.getDate(),
                    ds.getOwner().getName(),
                    p.getId(),
                    p.getName(),
                    ds.getNs(),
                    ds.__class__.__name__,
                ]
            )
    df = pd.DataFrame(data, columns=columns)
    return df


def image_exist(image_id, mm_dataset):
    image_found = False
    image_location = None
    index = None
    for k, v in DATASET_IMAGES[mm_dataset.__class__.__name__].items():
        if v:
            images_list = getattr(mm_dataset[k], v[0])
            if not isinstance(images_list, list):
                images_list = [images_list]
            for i, image in enumerate(images_list):
                if image_id == image.data_reference.omero_object_id:
                    image_found = True
                    image_location = k
                    index = i
                    break
    return image_found, image_location, index


def load_config_file_data(conn, project):
    setup = None
    for ann in project.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            ns = ann.getFile().getName()
            if ns.startswith("study_config"):
                setup = yaml.load(
                    ann.getFileInChunks().__next__().decode(),
                    Loader=yaml.SafeLoader,
                )
    return setup


def load_project(
    conn: BlitzGateway, project_id: int
) -> mm_schema.MetricsDatasetCollection:
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
                yaml_loader.loads(
                    file_ann.getFileInChunks().__next__().decode(),
                    target_class=getattr(mm_schema, ds_type),
                )
            )
        return collection
    except Exception as e:
        logger.error(f"Error loading project {project_id}: {e}")
        return collection


def load_dataset(
    dataset: DatasetWrapper, load_images: bool = True
) -> mm_schema.MetricsDataset:
    mm_datasets = []
    for ann in dataset.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            ns = ann.getNs()
            if ns.startswith("microscopemetrics_schema:analyses"):
                ds_type = ns.split("/")[-1]
                if ds_type in DATASET_TYPES:
                    mm_datasets.append(
                        yaml_loader.loads(
                            ann.getFileInChunks().__next__().decode(),
                            target_class=getattr(mm_schema, ds_type),
                        )
                    )
    if len(mm_datasets) == 1:
        mm_dataset = mm_datasets[0]
    elif len(mm_datasets) > 1:
        logger.warning(
            f"More than one dataset"
            f"found in dataset {dataset.getId()}."
            f"Using the first one"
        )
        mm_dataset = mm_datasets[0]
    else:
        logger.info(f"No dataset found in dataset {dataset.getId()}")
        return None

    if load_images and mm_dataset.__class__.__name__ != "PSFBeadsDataset":
        # First time loading the images the
        # dataset does not know which images to load
        if mm_dataset.processed:
            input_images = getattr(
                mm_dataset.input_data,
                INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__],
            )
            for input_image in input_images:
                image_wrapper = omero_tools.get_omero_obj_from_mm_obj(
                    dataset._conn, input_image
                )
                input_image.array_data = _load_image_intensities(image_wrapper)
        else:
            input_images = [
                load_image(image) for image in dataset.listChildren()
            ]
            setattr(
                mm_dataset,
                INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__],
                input_images,
            )
    else:
        setattr(
            mm_dataset, INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__], []
        )

    return mm_dataset


def load_dash_data_image(
    conn: BlitzGateway,
    mm_dataset: mm_schema.MetricsDataset,
    image: mm_schema.Image,
    image_index: int,
    image_location: str,
) -> dict:
    dash_context = {}
    if (
        isinstance(mm_dataset, FieldIlluminationDataset)
        and image_location == "input_data"
    ):
        dash_context["image"] = image.array_data
        dash_context["channel_names"] = image.channel_series
        ann_id = mm_dataset.output.__dict__["intensity_profiles"][
            image_index
        ].data_reference.omero_object_id
        # roi_service = conn.getRoiService()
        # result = roi_service.findByImage(
        #     int(image.data_reference.omero_object_id), None, conn.SERVICE_OPTS
        # )
        # shapes_rectangle, shapes_line, shapes_point = get_rois_omero(result)
        image_id = int(image.data_reference.omero_object_id)
        rois = get_rois_mm_dataset(mm_dataset)
        df_lines_omero = pd.DataFrame(rois[image_id]["roi"]["Line"])
        df_rects_omero = pd.DataFrame(rois[image_id]["roi"]["Rectangle"])
        df_points_omero = pd.DataFrame(rois[image_id]["roi"]["Point"])
        df_lines_omero.columns = df_lines_omero.columns.str.upper()
        df_rects_omero.columns = df_rects_omero.columns.str.upper()
        df_points_omero.columns = df_points_omero.columns.str.upper()
        dash_context["df_lines"] = df_lines_omero
        dash_context["df_rects"] = df_rects_omero
        dash_context["df_points"] = df_points_omero
        dash_context["df_intensity_profiles"] = get_table_file_id(conn, ann_id)
    elif (
        isinstance(mm_dataset, FieldIlluminationDataset)
        and image_location == "output"
    ):
        dash_context["image"] = image.array_data
        dash_context["channel_names"] = image.channel_series
        dash_context["message"] = (
            "No visualization available for output images."
        )
    elif (
        isinstance(mm_dataset, PSFBeadsDataset)
        and image_location == "input_data"
    ):
        dash_context["image"] = image.array_data
        dash_context["min_distance"] = (
            mm_dataset.input_parameters.min_lateral_distance_factor
        )
        dash_context["channel_names"] = image.channel_series
        dash_context["bead_properties_df"] = get_table_file_id(
            conn,
            mm_dataset.output.bead_properties.data_reference.omero_object_id,
        )

        dash_context["bead_km_df"] = get_table_file_id(
            conn,
            mm_dataset.output.key_measurements.data_reference.omero_object_id,
        )
        dash_context["bead_x_profiles_df"] = get_table_file_id(
            conn,
            mm_dataset.output.bead_profiles_x.data_reference.omero_object_id,
        )
        dash_context["bead_y_profiles_df"] = get_table_file_id(
            conn,
            mm_dataset.output.bead_profiles_y.data_reference.omero_object_id,
        )
        dash_context["bead_z_profiles_df"] = get_table_file_id(
            conn,
            mm_dataset.output.bead_profiles_z.data_reference.omero_object_id,
        )
        dash_context["image_id"] = image.data_reference.omero_object_id
    elif (
        isinstance(mm_dataset, PSFBeadsDataset) and image_location == "output"
    ):
        dash_context["image"] = image.array_data
        dash_context["channel_names"] = image.channel_series
        dash_context["message"] = (
            "No visualization available for output images."
        )

    else:
        dash_context = {}
    return dash_context


def load_dash_data_dataset(
    conn: BlitzGateway,
    dataset: mm_schema.MetricsDataset,
) -> dict:
    dash_context = {}

    if isinstance(dataset, FieldIlluminationDataset):
        title = "Field Illumination Dataset"

        dash_context["title"] = title
        dash_context["dm"] = dataset
        df = get_images_intensity_profiles(dataset)
        dash_context["image"], channel_series = concatenate_images(
            dataset.input_data.field_illumination_image
        )
        dash_context["channel_names"] = channel_series
        dash_context["intensity_profiles"] = get_all_intensity_profiles(
            conn, df
        )
        dash_context["key_values_df"] = get_table_file_id(
            conn,
            dataset.output.key_measurements.data_reference.omero_object_id,
        )
        dash_context["timeline_data"] = [
            {
                "name": i.name,
                "description": i.description,
                "acquisition_datetime": i.acquisition_datetime,
            }
            for i in dataset.input_data.field_illumination_image
        ]

    elif isinstance(dataset, PSFBeadsDataset):

        dash_context["bead_km_df"] = get_table_file_id(
            conn,
            dataset.output.key_measurements.data_reference.omero_object_id,
        )

    else:
        dash_context = {}
    return dash_context


def load_dash_data_project(
    conn: BlitzGateway,
    processed_datasets: dict,
) -> (dict, str):
    dash_context = {}
    app_name = "omero_project_dash"
    df_list = []
    kkm = list(processed_datasets.values())[0].kkm
    dates = []
    for key, value in processed_datasets.items():
        df = get_table_file_id(
            conn,
            value.mm_dataset.output.key_measurements.data_reference.omero_object_id,
        )
        date = datetime.strptime(
            value.mm_dataset.acquisition_datetime, "%Y-%m-%dT%H:%M:%S"
        )
        dates.append(date.date())
        df_list.append(df)
    dash_context["key_measurements_list"] = df_list
    dash_context["kkm"] = kkm
    dash_context["dates"] = dates
    return dash_context, app_name


def load_analysis_config(project=ProjectWrapper):
    configs = [
        ann
        for ann in project.listAnnotations(ns="OMERO-metrics/analysis_config")
        if isinstance(ann, MapAnnotationWrapper)
    ]
    if not configs:
        return None, None
    if len(configs) > 1:
        logger.error(
            f"More than one configuration"
            f" in project {project.getId()}."
            f"Using the last one saved"
        )

    return configs[-1].getId(), dict(configs[-1].getValue())


def load_image(
    image: ImageWrapper, load_array: bool = True
) -> mm_schema.Image:
    """Load an image from OMERO and return it as a schema Image"""
    time_series = None
    channel_series = mm_schema.ChannelSeries(
        channels=[
            {
                "name": c.getName(),
                "description": c.getDescription(),
                "data_reference": omero_tools.get_ref_from_object(c),
                "emission_wavelength_nm": c.getEmissionWave(),
                "excitation_wavelength_nm": c.getExcitationWave(),
            }
            for c in image.getChannels()
        ]
    )
    source_images = []
    array_data = _load_image_intensities(image) if load_array else None
    return mm_schema.Image(
        name=image.getName(),
        description=image.getDescription(),
        data_reference=omero_tools.get_ref_from_object(image),
        shape_x=image.getSizeX(),
        shape_y=image.getSizeY(),
        shape_z=image.getSizeZ(),
        shape_c=image.getSizeC(),
        shape_t=image.getSizeT(),
        acquisition_datetime=image.getAcquisitionDate(),
        voxel_size_x_micron=image.getPixelSizeX(),
        voxel_size_y_micron=image.getPixelSizeY(),
        voxel_size_z_micron=image.getPixelSizeZ(),
        time_series=time_series,
        channel_series=channel_series,
        source_images=source_images,
        # OMERO order zctyx -> microscope-metrics order TZYXC
        array_data=array_data,
    )


def _load_image_intensities(image: ImageWrapper) -> np.ndarray:
    return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))


def load_dataset_data(
    conn: BlitzGateway, dataset: DatasetWrapper
) -> mm_schema.MetricsDataset:
    pass


def get_project_data(
    collections: mm_schema.MetricsDatasetCollection,
) -> pd.DataFrame:
    data = []
    for dataset in collections.datasets:
        data.append(
            [
                dataset.__class__.__name__,
                dataset.data_reference.omero_object_type,
                dataset.data_reference.omero_object_id,
                dataset.processed,
                dataset.acquisition_datetime,
            ]
        )
    df = pd.DataFrame(
        data,
        columns=[
            "Analysis_type",
            "Omero_object_type",
            "Omero_object_id",
            "Processed",
            "Acquisition_datetime",
        ],
    )
    return df


def get_dataset_by_id(
    collections: mm_schema.MetricsDatasetCollection, dataset_id
) -> mm_schema.MetricsDataset:
    try:
        dataset = [
            i
            for i in collections.datasets
            if i.data_reference.omero_object_id == dataset_id
        ][0]
        return dataset
    except IndexError:
        return None


def get_images_intensity_profiles(
    dataset: mm_schema.MetricsDataset,
) -> pd.DataFrame:
    data = []
    for i, j in zip(
        dataset.input_data["field_illumination_image"],
        dataset.output["intensity_profiles"],
    ):
        data.append(
            [
                i["data_reference"]["omero_object_id"],
                j["data_reference"]["omero_object_id"],
                i["shape_c"],
            ]
        )
    df = pd.DataFrame(
        data,
        columns=["Field_illumination_image", "Intensity_profiles", "Channel"],
    )
    return df


def get_key_values(var: FieldIlluminationDataset.output) -> pd.DataFrame:
    data_dict = var.key_measurements.__dict__
    col = var.key_measurements.channel_name
    data_dict = [
        [key] + value
        for key, value in data_dict.items()
        if isinstance(value, list)
        and key
        not in [
            "name",
            "description",
            "data_reference",
            "linked_references",
            "channel_name",
        ]
    ]
    df = pd.DataFrame(data_dict, columns=["Measurements"] + col)
    return df


# def concatenate_images(images: list):
#     if len(images) > 1:
#         image_array_0 = images[0].array_data
#         channels = images[0].channel_series
#         result = image_array_0
#         for i in range(1, len(images)):
#             image_array = images[i].array_data
#             channels.channels.extend(images[i].channel_series.channels)
#             result = np.concatenate((result, image_array), axis=-1)
#         return result, channels
#     elif len(images) == 1:
#         return images[0].array_data, images[0].channel_series
#     else:
#         return None


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


def get_all_intensity_profiles(conn, data_df):
    df_01 = pd.DataFrame()
    for i, row in data_df.iterrows():
        file_id = (
            conn.getObject("FileAnnotation", row.Intensity_profiles)
            .getFile()
            .getId()
        )
        data = get_table_original_file_id(conn, str(file_id))
        for j in range(row.Channel):
            regx_find = f"ch0{j}"
            ch = i + j
            regx_repl = f"Ch0{ch}"
            data.columns = data.columns.str.replace(regx_find, regx_repl)
        df_01 = pd.concat([df_01, data], axis=1)
    return df_01


def get_table_file_id(conn, file_annotation_id):
    file_id = (
        conn.getObject("FileAnnotation", file_annotation_id).getFile().getId()
    )
    ctx = conn.createServiceOptsDict()
    ctx.setOmeroGroup("-1")
    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(file_id), ctx)
    data_buffer = collections.defaultdict(list)
    heads = t.getHeaders()
    target_cols = range(len(heads))
    index_buffer = []
    num_rows = t.getNumberOfRows()
    for start in range(0, num_rows):
        data = t.read(target_cols, start, start)
        for col in data.columns:
            data_buffer[col.name] += col.values
        index_buffer += data.rowNumbers
    df = pd.DataFrame.from_dict(data_buffer)
    df.index = index_buffer[0 : len(df)]
    return df


# -----------------------------------------------------------------------------------


def roi_finder(roi: mm_schema.Roi):
    if roi.rectangles:
        return {
            "type": "Rectangle",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": rect.name,
                    "x": rect.x,
                    "y": rect.y,
                    "w": rect.w,
                    "h": rect.h,
                }
                for rect in roi.rectangles
            ],
        }
    elif roi.lines:
        return {
            "type": "Line",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": line.name,
                    "x1": line.x1,
                    "y1": line.y1,
                    "x2": line.x2,
                    "y2": line.y2,
                }
                for line in roi.lines
            ],
        }
    elif roi.points:
        return {
            "type": "Point",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": point.name,
                    "x": point.x,
                    "y": point.y,
                    "c": point.c,
                }
                for point in roi.points
            ],
        }
    else:
        return None


def get_image_info_mm_dataset(mm_dataset: mm_schema.MetricsDataset):
    mm_images = getattr(
        mm_dataset["input_data"],
        DATASET_IMAGES[mm_dataset.class_name]["input_data"][0],
    )
    image_info = {
        i.data_reference.omero_object_id: {
            "name": i.name,
            "id": i.data_reference.omero_object_id,
            "n_channel": i.shape_c,
            "roi": {"Rectangle": [], "Line": [], "Point": []},
        }
        for i in mm_images
    }
    return image_info


def get_rois_mm_dataset(mm_dataset: mm_schema.MetricsDataset):
    images_info = get_image_info_mm_dataset(mm_dataset)
    output = mm_dataset.output
    for i, item in enumerate(images_info.items()):
        for field in output:
            if (
                isinstance(output[field], mm_schema.Roi)
                and isinstance(output[field].linked_references, list)
                and len(output[field].linked_references) == len(images_info)
            ):
                roi = roi_finder(output[field])
                if roi:
                    images_info[item[0]]["roi"][roi["type"]].extend(
                        roi["data"]
                    )
            elif (
                isinstance(output[field], list)
                and len(output[field]) == len(images_info)
                and isinstance(output[field][i], mm_schema.Roi)
            ):
                roi = roi_finder(output[field][i])
                if roi:
                    images_info[item[0]]["roi"][roi["type"]].extend(
                        roi["data"]
                    )
    return images_info
