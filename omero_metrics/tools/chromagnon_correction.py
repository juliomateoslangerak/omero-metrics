"""Chromagnon correction files stored in OMERO.

The chromatic shift analysis attaches its correction file (.chromagnon.csv, or
.chromagnon.tif with the local distortion map) to the dataset, with the
namespace ``namespaces.NS_CHROMAGNON_CORRECTION`` (see dump._dump_correction_file).
"""

import os
import tempfile

from microscopemetrics.analyses import chromagnon_apply
from omero.gateway import BlitzGateway, DatasetWrapper

from omero_metrics.tools import namespaces


# Name parts of the images the chromatic shift analysis creates (corrected
# images, distortion magnitude maps, the combined reference); these are outputs,
# not inputs for an analysis or a correction.
OUTPUT_NAME_MARKERS = ("_ALN", "_local_distortion_magnitude_", "_combined_reference")


def is_output_name(name: str) -> bool:
    """True for the name of an image created by the chromatic shift analysis."""
    return any(m in (name or "") for m in OUTPUT_NAME_MARKERS)


def _cache_dir() -> str:
    path = os.path.join(tempfile.gettempdir(), "omero_metrics_chromagnon_correction")
    os.makedirs(path, exist_ok=True)
    return path


def dataset_correction_ann_id(dataset: DatasetWrapper):
    """Id of the correction file attached to ``dataset`` by the analysis, or None."""
    for ann in dataset.listAnnotations(ns=namespaces.NS_CHROMAGNON_CORRECTION):
        return int(ann.getId())
    return None


def download_correction(conn: BlitzGateway, ann_id: int) -> str:
    """Download a correction file annotation and return the local path.

    The file keeps its name (Chromagnon reads .csv and .tif files differently)
    and is cached per annotation id.
    """
    ann = conn.getObject("FileAnnotation", int(ann_id))
    if ann is None:
        raise ValueError(f"Correction file {ann_id} was not found.")
    name = os.path.basename(ann.getFile().getName())
    if not chromagnon_apply.is_correction_filename(name):
        # Keep the extension Chromagnon needs to tell a .csv from a .tif.
        name = name + chromagnon_apply.CORRECTION_SUFFIXES[0]
    folder = os.path.join(_cache_dir(), str(int(ann_id)))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        tmp = path + ".part"
        with open(tmp, "wb") as fh:
            for chunk in ann.getFileInChunks():
                fh.write(chunk)
        os.replace(tmp, path)
    return path
