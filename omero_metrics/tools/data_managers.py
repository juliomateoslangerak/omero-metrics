import datetime
import logging

from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema,
)
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
)
from omero_metrics.tools import load, dump, update, delete
from omero_metrics.tools.data_type import (
    KKM_MAPPINGS,
    TEMPLATE_MAPPINGS_DATASET,
    TEMPLATE_MAPPINGS_IMAGE,
)


logger = logging.getLogger(__name__)


def warning_message(msg):
    dash_context = {"message": msg}
    app_name = "WarningApp"
    return dash_context, app_name


class ImageManager:
    """This class is a unit of work that processes
    data from an image (OMERO-metrics).
    """

    def __init__(self, conn: BlitzGateway, omero_image: ImageWrapper):
        self._conn = conn
        if isinstance(omero_image, ImageWrapper):
            self.omero_image = omero_image
        else:
            raise ValueError("the object must be an ImageWrapper")
        self.omero_image = omero_image
        self.omero_dataset = self.omero_image.getParent()
        self.dataset_manager = DatasetManager(
            self._conn, self.omero_dataset, False
        )
        self.context = {}
        self.mm_image = None
        self.image_exist = None
        self.image_index = None
        self.image_location = None
        self.app_name = None

    def load_data(self, force_reload=True):
        logger.info("Loading data CALL")
        if force_reload or self.mm_image is None:
            self.dataset_manager.load_data()
            if self.dataset_manager.processed:
                self.mm_image = load.load_image(self.omero_image)
                self.dataset_manager.remove_unsupported_data()
            else:
                self.mm_image = None
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def visualize_data(self):
        if self.dataset_manager.processed:
            if (
                self.dataset_manager.mm_dataset.__class__.__name__
                in TEMPLATE_MAPPINGS_DATASET
            ):
                (
                    self.image_exist,
                    self.image_location,
                    self.image_index,
                ) = load.image_exist(
                    self.omero_image.getId(), self.dataset_manager.mm_dataset
                )
                if self.image_exist:
                    self.app_name = TEMPLATE_MAPPINGS_IMAGE.get(
                        self.dataset_manager.mm_dataset.__class__.__name__
                    )[self.image_location]
                    if self.image_location == "input_data":
                        self.context = {
                            "image_index": self.image_index,
                            "image_id": self.mm_image.data_reference.omero_object_id,
                            "mm_dataset": self.dataset_manager.mm_dataset,
                            "channel_names": self.mm_image.channel_series,
                            "image": self.mm_image.array_data,
                        }
                    elif self.image_location == "output":
                        message = "No visualization for output images"
                        logger.warning(message)
                        self.context, self.app_name = warning_message(message)
                else:
                    message = "Image does not exist in the dataset yaml file. Unable to visualize"
                    logger.warning(message)
                    self.context, self.app_name = warning_message(message)
            else:
                message = "Unknown analysis type. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)
        else:
            message = "Dataset has not been processed. Unable to visualize"
            logger.warning(message)
            self.context, self.app_name = warning_message(message)


class DatasetManager:
    """
    This class is a unit of work that processes
    data from a dataset or a dataset_collection (OMERO-metrics)
    It contains the data (microscope-metrics_schema
    datasets and dataset_collections) and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(
        self,
        conn: BlitzGateway,
        omero_dataset: DatasetWrapper,
        load_images=False,
    ):
        self._conn = conn
        if isinstance(omero_dataset, DatasetWrapper):
            self.omero_dataset = omero_dataset
        else:
            raise ValueError("dataset must be a DatasetWrapper")
        self.omero_project = self.omero_dataset.getParent()
        self.input_parameters = None
        self.load_images = load_images
        self.mm_dataset = None
        self.analysis_config = None
        self.analysis_config_id = None
        self.analysis_func = None
        self.app_name = None
        self.context = {}
        self.processed = False
        self.microscope = mm_schema.Microscope()
        self.kkm = None
        self.attached_images = [
            {"value": f"{i.getId()}", "label": f"{i.getName()}"}
            for i in omero_dataset.listChildren()
            if i.OMERO_CLASS == "Image"
        ]

    def is_processed(self):
        self.processed = (
            self.mm_dataset.processed if self.mm_dataset else False
        )
        return self.processed

    def is_validated(self):
        return self.mm_dataset.validated if self.mm_dataset else False

    def remove_unsupported_data(self):
        dump._remove_unsupported_types(self.mm_dataset.input_data)
        dump._remove_unsupported_types(self.mm_dataset.input_parameters)
        dump._remove_unsupported_types(self.mm_dataset.output)

    def load_data(self, force_reload=True):
        if force_reload or self.mm_dataset is None:
            self.mm_dataset = load.load_dataset(
                self.omero_dataset, self.load_images
            )
            self.kkm = KKM_MAPPINGS.get(self.mm_dataset.__class__.__name__)
            self.processed = (
                self.mm_dataset.processed if self.mm_dataset else False
            )
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def load_analysis_config(self, force_reload=True):
        if (
            not force_reload
            and self.analysis_config
            and self.analysis_config_id
        ):
            return
        else:
            (
                self.analysis_config_id,
                self.analysis_config,
            ) = load.load_analysis_config(self.omero_project)

    def dump_analysis_config(self):
        if not self.analysis_config:
            logger.error("No configuration to save.")
            return

        update.update_key_measurements(
            conn=self._conn,
            new_key_measurements=self.analysis_config,
            target_key_measurements=self.analysis_config_id,
            replace=True,
            new_description=f"config saved on {datetime.datetime.now()}",
        )
        logger.info(
            f"Saved configuration on mapAnn id:{self.analysis_config_id}"
        )

    def _update_dataset_input_config(self, config):
        for key, val in config.items():
            setattr(self.mm_dataset.input_parameters, key, val)

    def dump_data(self):
        for mm_ds in self.mm_dataset:
            if not mm_ds.processed:
                logger.error("Dataset not processed. Unable to dump data")
            dump.dump_dataset(
                conn=self._conn,
                dataset=mm_ds,
                target_project=self.omero_project,
            )

    def process_data(self, force_reprocess=False):
        if not force_reprocess and self.is_processed():
            if self.is_validated():
                logger.warning(
                    "Dataset has been processed and validated. "
                    "Force reprocess to process again"
                )
            else:
                logger.warning(
                    "Dataset has been processed but not validated. "
                    "Force reprocess to process again"
                )
            return False
        items_to_remove = []
        config = {
            k: v
            for k, v in self.analysis_config.items()
            if k not in items_to_remove
        }

        self._update_dataset_input_config(config)
        self.analysis_func(self.mm_dataset)

        return True

    def delete_processed_data(self, conn: BlitzGateway):
        """This function deletes the output of the dataset"""
        logger.debug(
            f"Deleting processed data for dataset {self.omero_dataset.getId()}"
        )
        if not self.processed:
            logger.warning("Data has not been processed. Nothing to delete")
            return
        try:
            delete.delete_mm_obj_omero_refs(conn, self.mm_dataset.output)
            delete.delete_dataset_file_ann(conn, self.omero_dataset)
        except Exception as e:
            logger.error(f"Error deleting processed data: {e}")
            self.mm_dataset.validated = False
            raise e
        else:
            logger.info("Processed data deleted.")

    def process_data_remotely(self):
        pass

    def validate_data(self):
        if not self.mm_dataset.processed:
            logger.error("Data has not been processed. It cannot be validated")
        if self.mm_dataset.validated:
            logger.warning("Data was already validated. Keeping unchanged.")

        self.mm_dataset.validated = True
        logger.info("Validating dataset.")

    def invalidate_data(self):
        if not self.mm_dataset.validated:
            logger.warning("Data is already not validated. Keeping unchanged.")
        self.mm_dataset.validated = False
        logger.info("Invalidating dataset.")

    def visualize_data(self):
        if self.processed:
            if self.mm_dataset.__class__.__name__ in TEMPLATE_MAPPINGS_DATASET:
                self.app_name = TEMPLATE_MAPPINGS_DATASET.get(
                    self.mm_dataset.__class__.__name__
                )

                if isinstance(
                    self.mm_dataset, mm_schema.FieldIlluminationDataset
                ):
                    self.context["image"], self.context["channel_names"] = (
                        load.concatenate_images(
                            self.mm_dataset.input_data.field_illumination_images
                        )
                    )
                    self.remove_unsupported_data()
                self.context["mm_dataset"] = self.mm_dataset
                self.context["kkm"] = self.kkm

            else:
                message = "Unknown analysis type. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)
        else:
            if self.omero_project and len(self.attached_images) > 0:
                self.input_parameters = load.load_config_file_data(
                    self.omero_project
                )
                if self.input_parameters:
                    self.app_name = "omero_dataset_form"
                    self.context = {
                        "list_images": self.attached_images,
                        "input_parameters": self.input_parameters,
                        "dataset_id": self.omero_dataset.getId(),
                    }
                else:
                    message = "No, config file detected. Click on the project parent to load the config file."
                    logger.warning(message)
                    self.context, self.app_name = warning_message(message)
            else:
                message = "The dataset is not under a project or does not contain images. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)


class ProjectManager:
    """
    This class is a unit of work that processes
    data from a project (OMERO-metrics)
    It contains the data and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(self, conn: BlitzGateway, omero_project: ProjectWrapper):
        self._conn = conn
        self.omero_project = omero_project
        self.datasets = []
        self.context = {}
        self.setup = None
        self.threshold = None
        self.datasets_types = []
        self.processed_datasets = {}
        self.unprocessed_datasets = {}
        self.app_name = None
        self.homogenize = None
        self.mm_harmonized_dataset = None

    def load_data(self, force_reload=True):
        if force_reload or self.datasets is []:
            for dataset in self.omero_project.listChildren():
                dm = DatasetManager(self._conn, dataset)
                dm.load_data()
                dm.is_processed()
                self.datasets_types.append(dm.mm_dataset.__class__.__name__)
                self.datasets.append(dm)
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def check_processed_data(self):
        for dataset in self.datasets:
            if dataset.processed:
                self.processed_datasets[dataset.omero_dataset.getId()] = (
                    dataset
                )
            else:
                self.unprocessed_datasets[dataset.omero_dataset.getId()] = (
                    dataset
                )

    def is_homogenized(self):
        unique = set(
            [
                dataset.mm_dataset.__class__.__name__
                for dataset in self.processed_datasets.values()
            ]
        )
        if len(unique) == 1:
            self.homogenize = True
        else:
            self.homogenize = False
        return self.homogenize

    def visualize_data(self):
        if self.setup:
            if self.processed_datasets and self.is_homogenized():
                if (
                    list(self.processed_datasets.values())[
                        0
                    ].mm_dataset.__class__.__name__
                    in TEMPLATE_MAPPINGS_DATASET
                ):
                    self.context = load.load_dash_data_project(
                        self.processed_datasets
                    )
                    self.context["unprocessed_datasets"] = list(
                        self.unprocessed_datasets.keys()
                    )
                    self.context["datasets_types"] = self.datasets_types
                    self.context["processed_datasets"] = list(
                        self.processed_datasets.keys()
                    )
                    self.mm_harmonized_dataset = (
                        mm_schema.HarmonizedMetricsDatasetCollection(
                            datasets=[
                                dm.mm_dataset
                                for dm in self.datasets
                                if dm.processed
                            ],
                            dataset_class=self.datasets[
                                0
                            ].mm_dataset.class_name,
                            name=self.omero_project.getName(),
                            description=self.omero_project.getDescription(),
                        )
                    )
                    self.context["mm_datasets"] = self.mm_harmonized_dataset
                    message = "Data loaded successfully"
                else:
                    message = "This project contains unsupported analysis type. Unable to visualize"
                    logger.warning(message)
            else:
                message = "No data or compatible data to visualize. Please process the data first."
                logger.warning(message)
            self.context["message"] = message
            self.context["setup"] = self.setup
            self.context["threshold"] = (
                self.threshold if self.threshold else ""
            )
            self.app_name = "omero_project_dash"
        else:
            self.app_name = "omero_project_config_form"
            self.context = {}

    def save_settings(self):
        pass

    def delete_data(self):
        pass

    def delete_processed_data(self):
        for dataset in self.datasets:
            if dataset.processed:
                dataset.delete_processed_data(self._conn)

    def load_config_file(self):
        if self.setup is None:
            self.setup = load.load_config_file_data(self.omero_project)

    def load_threshold_file(self):
        if self.threshold is None:
            self.threshold = load.load_thresholds_file_data(self.omero_project)


class MicroscopeManager:
    """
    This class is a unit of work that processes
    data from a microscope (OMERO-metrics)
    It contains the data and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(self, conn: BlitzGateway, microscope_id: int):
        self._conn = conn
        self.microscope_id = microscope_id
        self.microscope = conn.getObject("Microscope", microscope_id)
        self.data = None
        self.context = None

    def visualize_data(self):
        pass

    def save_settings(self):
        pass

    def delete_data(self):
        pass
