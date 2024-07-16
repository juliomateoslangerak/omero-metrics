import datetime
import logging
from typing import Union
from microscopemetrics.samples import field_illumination, psf_beads
from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema,
)
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
)
from . import load, dump, update, delete

logger = logging.getLogger(__name__)


ANALYSIS_MAPPINGS = {
    "analise_field_illumination": field_illumination.analise_field_illumination,
    "analyse_psf_beads": psf_beads.analyse_psf_beads,
}

SAMPLE_MAPPINGS = {
    "FieldIllumination": field_illumination,
    "PSFBeads": psf_beads,
}

DATASET_MAPPINGS = {
    "FieldIlluminationDataset": mm_schema.FieldIlluminationDataset,
    "PSFBeadsDataset": mm_schema.PSFBeadsDataset,
}

INPUT_MAPPINGS = {
    "FieldIlluminationInput": mm_schema.FieldIlluminationInput,
    "PSFBeadsInput": mm_schema.PSFBeadsInput,
}

OBJECT_TO_DUMP_FUNCTION = {
    mm_schema.Image: dump.dump_image,
    mm_schema.Roi: dump.dump_roi,
    mm_schema.Tag: dump.dump_tag,
    mm_schema.KeyValues: dump.dump_key_values,
    mm_schema.Table: dump.dump_table,
}

TEMPLATE_MAPPINGS_DATASET = {
    "FieldIlluminationDataset": "OMERO_metrics/omero_views/center_view_dataset_foi.html",
    "PSFBeadsDataset": "OMERO_metrics/omero_views/center_view_dataset_psf_beads.html",
    "unknown_analysis": "OMERO_metrics/omero_views/center_view_unknown_analysis_type.html",
    "unprocessed_analysis": "OMERO_metrics/omero_views/unprocessed_dataset.html",
    "image_not_found": "OMERO_metrics/omero_views/image_not_found_dataset.html",
}

TEMPLATE_MAPPINGS_IMAGE = {
    "FieldIlluminationDataset": {
        "input": "OMERO_metrics/omero_views/center_view_image.html",
        "output": "OMERO_metrics/omero_views/unprocessed_dataset.html",
    },
    "PSFBeadsDataset": {
        "input": "OMERO_metrics/omero_views/center_view_image_psf.html",
        "output": "OMERO_metrics/omero_views/unprocessed_dataset.html",
    },
}


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
        self.dataset_manager = DatasetManager(self._conn, self.omero_dataset)
        self.context = None
        self.mm_image = None
        self.image_exist = None
        self.image_index = None
        self.image_location = None
        self.template = None

    def load_data(self, force_reload=True):
        if force_reload or self.mm_image is None:
            self.mm_image = load.load_image(self.omero_image)
            self.dataset_manager.load_data()
            self.dataset_manager.is_processed()
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
                    self.template = TEMPLATE_MAPPINGS_IMAGE.get(
                        self.dataset_manager.mm_dataset.__class__.__name__
                    )[self.image_location]
                    self.context = load.load_dash_data_image(
                        self._conn,
                        self.dataset_manager.mm_dataset,
                        self.mm_image,
                        self.image_index,
                        self.image_location,
                    )
                else:
                    logger.warning(
                        "Image does not exist in the dataset yaml file. Unable to visualize"
                    )
                    self.template = TEMPLATE_MAPPINGS_DATASET.get(
                        "image_not_found"
                    )
                    self.context = {}
            else:
                logger.warning("Unknown analysis type. Unable to visualize")
                self.template = TEMPLATE_MAPPINGS_DATASET.get(
                    "unknown_analysis"
                )
                self.context = {}
        else:
            logger.warning(
                "Dataset has not been processed. Unable to visualize"
            )
            self.template = TEMPLATE_MAPPINGS_DATASET.get(
                "unprocessed_analysis"
            )
            self.context = {}


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
            raise ValueError("datasets must be a DatasetWrapper")

        self.omero_project = self.omero_dataset.getParent()
        self.load_images = load_images
        self.mm_dataset = None
        self.analysis_config = None
        self.analysis_config_id = None
        self.analysis_func = None
        self.template = None
        self.context = None
        self.processed = False
        self.microscope = mm_schema.Microscope()

    def is_processed(self):
        if self.mm_dataset:
            self.processed = self.mm_dataset.processed
        else:
            self.processed = False

    def is_validated(self):
        return self.mm_dataset.validated if self.mm_dataset else False

    def load_data(self, force_reload=True):
        if force_reload or self.mm_dataset is None:
            self.mm_dataset = load.load_dataset(
                self.omero_dataset, self.load_images
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
            self.analysis_config_id, self.analysis_config = (
                load.load_analysis_config(self.omero_project)
            )

    def dump_analysis_config(self):
        if not self.analysis_config:
            logger.error("No configuration to save.")
            return

        update.update_key_value(
            conn=self._conn,
            new_key_values=self.analysis_config,
            target_key_values=self.analysis_config_id,
            replace=True,
            new_description=f"config saved on {datetime.datetime.now()}",
        )
        logger.info(
            f"Saved configuration on mapAnn id:{self.analysis_config_id}"
        )

    def _update_dataset_input_config(self, config):
        for key, val in config.items():
            setattr(self.mm_dataset.input, key, val)

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

    def delete_processed_data(self):
        """This function deletes the output of the dataset"""
        if not self.is_processed():
            logger.warning("Data has not been processed. Nothing to delete")
            return False
        try:
            logger.warning("Deleting processed data...")
            delete.delete_dataset_output(self._conn, self.mm_dataset)
            self.mm_dataset.validated = False
            self.mm_dataset.processed = False
        except Exception as e:
            logger.error(f"Error deleting processed data: {e}")
            self.mm_dataset.validated = False
            return False

        return True

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
                self.template = TEMPLATE_MAPPINGS_DATASET.get(
                    self.mm_dataset.__class__.__name__
                )
                self.context = load.load_dash_data_dataset(
                    self._conn, self.mm_dataset
                )
            else:
                logger.warning("Unknown analysis type. Unable to visualize")
                self.template = TEMPLATE_MAPPINGS_DATASET.get(
                    "unknown_analysis"
                )
                self.context = {}
        else:
            logger.warning(
                "Dataset has not been processed. Unable to visualize"
            )
            self.template = TEMPLATE_MAPPINGS_DATASET.get(
                "unprocessed_analysis"
            )
            self.context = {}

    def save_settings(self):
        pass

    def delete_data(self):
        pass


class ProjectManager:
    """
    This class is a unit of work that processes
    data from a project (OMERO-metrics)
    It contains the data and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(self, conn: BlitzGateway, project: ProjectWrapper):
        self._conn = conn
        self.project = project
        self.datasets = []
        self.context = None

    def load_data(self, force_reload=True):
        if force_reload or self.datasets is None:
            for dataset in self.project.listChildren():
                dm = DatasetManager(self._conn, dataset)
                dm.load_data()
                dm.is_processed()
                self.datasets.append(dm)
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def visualize_data(self):
        pass

    def save_settings(self):
        pass

    def delete_data(self):
        pass


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

    def load_data(self, force_reload=True):
        if force_reload or self.data is None:
            self.data = load.load_microscope(self._conn, self.microscope_id)
            self.context = self.data["context"]
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def visualize_data(self):
        pass

    def save_settings(self):
        pass

    def delete_data(self):
        pass
