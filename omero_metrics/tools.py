import pandas as pd

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