import datetime
import logging
from typing import Union

from microscopemetrics.samples import (
    field_illumination,
    psf_beads
)
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper, ProjectWrapper

from omero_metrics.tools import load, dump, update, delete

logger = logging.getLogger(__name__)

ANALYSIS_MAPPINGS = {
    "analise_field_illumination": field_illumination.analise_field_illumination,
    "analyse_psf_beads": psf_beads.analyse_psf_beads,
}

SAMPLE_MAPPINGS = {
    "FieldIllumination": field_illumination,
    "PSFBeads": psf_beads
}

DATASET_MAPPINGS = {
    "FieldIlluminationDataset": mm_schema.FieldIlluminationDataset,
    "PSFBeadsDataset": mm_schema.PSFBeadsDataset
}

INPUT_MAPPINGS = {
    "FieldIlluminationInput": mm_schema.FieldIlluminationInput,
    "PSFBeadsInput": mm_schema.PSFBeadsInput,
}


OBJECT_TO_DUMP_FUNCTION = {
    mm_schema.Image: dump.dump_image,
    mm_schema.Roi: dump.dump_roi,
    mm_schema.Tag: dump.dump_tag,
    mm_schema.KeyValues: dump.dump_key_value,
    mm_schema.Table: dump.dump_table,
}


class DatasetManager:
    """
    This class is a unit of work that processes data from a dataset or a dataset_collection (OMERO-project)
    It contains the data (microscope-metrics_schema datasets and dataset_collections) and the necessary methods
    to interact with OMERO and load and dump data.
    """
    def __init__(self, conn: BlitzGateway, dataset: Union[DatasetWrapper, int]):
        self._conn = conn
        if isinstance(dataset, DatasetWrapper):
            self.omero_dataset = dataset
        elif isinstance(dataset, int):
            self.omero_dataset = self._conn.getObject("Dataset", dataset)
        else:
            raise ValueError("datasets must be a DatasetWrapper or a dataset id")

        self.omero_project = self.omero_dataset.getParent()
        self.mm_dataset = None
        self.analysis_config = None
        self.analysis_config_id = None
        self.analysis_func = None
        self.microscope = mm_schema.Microscope()  # TODO: top it up!!

    def is_processed(self):
        return self.mm_dataset.processed if self.mm_dataset else False

    def is_validated(self):
        return self.mm_dataset.validated if self.mm_dataset else False

    def load_data(self, force_reload=True):
        # TODO: If a user deletes the images but not the whole dataset and attachments,
        #  there is the possibility to read invalid data. Take into account
        if force_reload or self.mm_dataset is None:
            self.mm_dataset = load.load_dataset(self.omero_dataset)
        else:
            raise NotImplementedError("partial loading of data from OMERO is not yet implemented")

    def load_analysis_config(self, force_reload=True):
        if not force_reload and self.analysis_config and self.analysis_config_id:
            return
        else:
            self.analysis_config_id, self.analysis_config = load.load_analysis_config(self.omero_project)

    def save_analysis_config(self):
        if not self.analysis_config:
            logger.error("No configuration to save.")
            return

        update.update_key_value(
            conn=self._conn,
            new_key_values=self.analysis_config,
            target_key_values=self.analysis_config_id,
            replace=True,
            new_description=f"config saved on {datetime.datetime.now()}"
        )
        logger.info(f"Saved configuration on mapAnn id:{self.analysis_config_id}")

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
                target_project=self.omero_project
            )

    def process_data(self, force_reprocess=False):
        if not force_reprocess and self.is_processed():
            if self.is_validated():
                logger.warning("Dataset has been processed and validated. Force reprocess to process again")
            else:
                logger.warning("Dataset has been processed but not validated. Force reprocess to process again")
            return False
        items_to_remove = []
        config = {k:v for k, v in self.analysis_config.items() if k not in items_to_remove}

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

    def save_settings(self):
        pass

    def delete_data(self):
        pass
