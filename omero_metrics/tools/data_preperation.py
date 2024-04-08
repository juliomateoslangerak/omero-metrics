import pandas as pd


def get_dataset_ids_lists(conn, project_id):
    """
    Get the processed and unprocessed dataset ids for a project
    """
    processed_datasets = []
    unprocessed_datasets = []
    project = conn.getObject("Project", project_id)
    for dataset in project.listChildren():
        try:
            dataset.getAnnotation().getNs()
            processed_datasets.append(dataset.getId())
        except AttributeError:
            unprocessed_datasets.append(dataset.getId())
    return processed_datasets, unprocessed_datasets



def get_dataset_mapAnnotation(conn, dataset_id):
    """
    Get the mapAnnotation for a dataset
    """
    dataset = conn.getObject("Dataset", dataset_id)
    try:
        for i in dataset.listAnnotations():
            if "FieldIlluminationKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
        return df
    except:
        return {}