import pandas as pd
from microscopemetrics_schema.datamodel.microscopemetrics_schema import (
    FieldIlluminationDataset,
)
import numpy as np
from microscopemetrics_omero import omero_tools
from omero.gateway import BlitzGateway, DatasetWrapper, _ProjectWrapper
from microscopemetrics_omero.load import load_image
from hypothesis import HealthCheck, given, settings
from microscopemetrics.strategies import strategies as st_mm
from microscopemetrics_omero.load import load_image
from .tools import *
from microscopemetrics_omero.dump import *
import omero


def info_row(obj):
    row = [obj.getId(), obj.OMERO_CLASS, obj.getName(), obj.getOwnerOmeName()]
    return row


def get_info_dash(conn):
    my_exp_id = conn.getUser().getId()
    default_group_id = conn.getEventContext().groupId
    list_PROJECTS = []
    list_DATASETS = []
    list_IMAGE = []
    for project in conn.getObjects("Project"):
        list_PROJECTS.append(info_row(project))
        for dataset in project.listChildren():
            list_DATASETS.append(info_row(dataset))
            for image in dataset.listChildren():
                list_IMAGE.append(info_row(image))
    df_project = pd.DataFrame(list_PROJECTS, columns=["ID", "OMERO_CLASS", "Name", "Owner"])
    df_dataset = pd.DataFrame(list_DATASETS, columns=["ID", "OMERO_CLASS", "Name", "Owner"])
    df_image = pd.DataFrame(list_IMAGE, columns=["ID", "OMERO_CLASS", "Name", "Owner"])

    return df_project, df_dataset, df_image


def get_intensity_map_data(var: FieldIlluminationDataset.output) -> None:
    # TZYXC
    list_ima = var.intensity_map.data
    x = var.intensity_map.shape_x
    y = var.intensity_map.shape_y
    z = var.intensity_map.shape_z
    t = var.intensity_map.shape_t
    c = var.intensity_map.shape_c
    ima = np.array(list_ima).reshape([t, z, y, x, c])
    # pil_ima = Image.fromarray(ima1)
    return ima


def data_loader(conn, number, new_project_name):
    @given(dataset=st_mm.st_field_illumination_dataset())
    @settings(max_examples=number, suppress_health_check=[HealthCheck.too_slow], deadline=10000)
    def getDataset(dataset, list_data):
        list_data.append(dataset)

    list_data = []
    getDataset(list_data)
    [_["unprocessed_analysis"].run() for _ in list_data]
    new_project = _ProjectWrapper(conn, omero.model.ProjectI())
    new_project.setName(new_project_name)
    new_project.save()
    for i in list_data:
        var = i["unprocessed_analysis"].output
        name = "Field Illumination " + str(i["unprocessed_analysis"].name)
        new_dataset = DatasetWrapper(conn, omero.model.DatasetI())
        new_dataset.setName(name)
        new_dataset.save()
        link = omero.model.ProjectDatasetLinkI()
        link.details.owner = omero.model.ExperimenterI(conn.getUser().getId(), False)
        link.setChild(omero.model.DatasetI(new_dataset.id, False))
        link.setParent(omero.model.ProjectI(new_project.id, False))
        conn.getUpdateService().saveObject(link, conn.SERVICE_OPTS)
        image_wrapper = dump_image(conn, var.intensity_map, new_dataset)
        image_wrapper = conn.getObject("Image", image_wrapper.id, opts={"datasets": [new_dataset.id]})
        dump_key_value(conn, var.key_values, image_wrapper)
        r = var.roi_profiles
        r_c = var.roi_corners
        r_w = var.roi_centroids_weighted
        dump_roi(conn, r, image_wrapper)
        dump_roi(conn, r_c, image_wrapper)
        dump_roi(conn, r_w, image_wrapper)
        dump_table(conn, var.intensity_profiles, image_wrapper)
    return True
