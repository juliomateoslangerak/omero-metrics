"""OMERO side of applying a saved Chromagnon correction to images (Phase 2).

The computation is in ``microscopemetrics.analyses.chromagnon_apply``. This
module finds the correction files in OMERO, downloads them, reads the target
images and uploads the corrected images next to them.

Correction files are file annotations that either
- were saved by the chromatic shift analysis (namespace
  ``namespaces.NS_CHROMAGNON_CORRECTION``), or
- are named ``*.chromagnon.csv`` / ``*.chromagnon.tif`` (e.g. made with the
  desktop Chromagnon and attached by hand).
"""

import datetime
import logging
import os

import omero
from microscopemetrics.analyses import chromagnon_apply as ca
from microscopemetrics.analyses import chromatic_shift
from omero.gateway import BlitzGateway
from omero.rtypes import rlist, rlong, rstring

from omero_metrics.tools import load, namespaces, omero_tools
from omero_metrics.tools.chromagnon_correction import (
    download_correction,
    is_output_name,
)

logger = logging.getLogger(__name__)

# Output images of the chromatic shift analysis and of this tool
# (chromagnon_correction.is_output_name) are listed as targets but not selected
# by default.
_PARENT_LINKS = (
    ("Dataset", "DatasetAnnotationLink"),
    ("Project", "ProjectAnnotationLink"),
    ("Image", "ImageAnnotationLink"),
)


def list_correction_files(conn: BlitzGateway) -> list:
    """Correction file annotations in the current group, newest first.

    Each item is a dict with ``id``, ``name``, ``saved_by_analysis``, ``date``
    and ``parents`` (e.g. ``["Dataset Beads_001 (51)"]``).
    """
    qs = conn.getQueryService()
    params = omero.sys.ParametersI()
    params.add("ns", rstring(namespaces.NS_CHROMAGNON_CORRECTION))
    params.add("csv", rstring("%" + ca.CORRECTION_SUFFIXES[0]))
    params.add("tif", rstring("%" + ca.CORRECTION_SUFFIXES[1]))
    rows = qs.projection(
        "select a.id, f.name, a.ns, a.details.creationEvent.time "
        "from FileAnnotation a join a.file f "
        "where a.ns = :ns or lower(f.name) like :csv or lower(f.name) like :tif "
        "order by a.details.creationEvent.time desc",
        params,
        conn.SERVICE_OPTS,
    )
    files = []
    for row in rows:
        ann_id, name, ns, time = (r.val if r is not None else None for r in row)
        files.append(
            {
                "id": int(ann_id),
                "name": name,
                "saved_by_analysis": ns == namespaces.NS_CHROMAGNON_CORRECTION,
                "date": (
                    datetime.datetime.fromtimestamp(time / 1000).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    if time
                    else ""
                ),
                "parents": [],
            }
        )
    if not files:
        return files

    by_id = {f["id"]: f for f in files}
    params = omero.sys.ParametersI()
    params.add("ids", rlist([rlong(i) for i in by_id]))
    for obj_type, link in _PARENT_LINKS:
        rows = qs.projection(
            f"select l.child.id, p.id, p.name from {link} l join l.parent p "
            "where l.child.id in (:ids)",
            params,
            conn.SERVICE_OPTS,
        )
        for row in rows:
            ann_id, pid, pname = (r.val for r in row)
            by_id[int(ann_id)]["parents"].append(f"{obj_type} {pname} ({pid})")
    return files


def correction_option_label(f: dict) -> str:
    where = ", ".join(f["parents"]) or "not linked"
    return f"{f['name']} — {where} — {f['date']}"


def list_target_images(conn: BlitzGateway, obj_type: str, ids: list) -> list:
    """Images to offer as targets for a selected dataset or selected images.

    Each item is a dict with ``id``, ``name``, ``dataset_id``, ``waves``,
    ``shape`` (T, Z, Y, X, C) and ``default`` (selected by default).
    """
    if obj_type == "dataset":
        dataset = conn.getObject("Dataset", int(ids[0]))
        if dataset is None:
            return []
        images = [(img, dataset.getId()) for img in dataset.listChildren()]
    else:
        images = []
        for i in ids:
            img = conn.getObject("Image", int(i))
            if img is not None:
                parent = img.getParent()
                images.append((img, parent.getId() if parent else None))

    targets = []
    for img, dataset_id in sorted(images, key=lambda x: x[0].getName() or ""):
        mm_image = load.load_image(img, load_array=False)
        targets.append(
            {
                "id": img.getId(),
                "name": img.getName(),
                "dataset_id": dataset_id,
                "waves": ca.image_waves(mm_image),
                "shape": [
                    img.getSizeT(),
                    img.getSizeZ(),
                    img.getSizeY(),
                    img.getSizeX(),
                    img.getSizeC(),
                ],
                "default": obj_type == "image" or not is_output_name(img.getName()),
            }
        )
    return targets


def check_targets(conn: BlitzGateway, info: dict, targets: list) -> dict:
    """Map image id -> list of reasons why the correction cannot be applied."""
    result = {}
    for t in targets:
        img = conn.getObject("Image", int(t["id"]))
        mm_image = load.load_image(img, load_array=False)
        result[t["id"]] = ca.check_compatibility(info, mm_image)
    return result


def apply_to_images(
    conn: BlitzGateway, ann_id: int, image_ids: list, echo=None, dataset_ids=None
) -> list:
    """Apply correction ``ann_id`` to ``image_ids``.

    Each corrected image is created as ``<root>_ALN.tif``, with the source
    image's metadata, in ``dataset_ids[image_id]`` (the dataset the image was
    listed from) or else in the first dataset of the source image. An image can
    be in several datasets, so the first one is not always the selected one.
    Returns one dict per
    image: ``image_id``, ``name``, ``ok``, ``message`` and, on success,
    ``new_image_id`` / ``new_name``.
    """

    def say(msg):
        logger.info(msg)
        if echo:
            echo(msg)

    path = download_correction(conn, ann_id)
    info = ca.read_correction_info(path)
    correction_name = os.path.basename(path)
    say(f"Correction {correction_name}: {ca.correction_label(info)}")

    chromatic_shift.set_echo_func(echo)
    results = []
    try:
        for n, image_id in enumerate(image_ids, start=1):
            img = conn.getObject("Image", int(image_id))
            if img is None:
                results.append(
                    {"image_id": image_id, "name": "?", "ok": False,
                     "message": "Image not found."}
                )
                continue
            name = img.getName()
            say(f"[{n}/{len(image_ids)}] {name}")
            try:
                mm_image = load.load_image(img, load_array=True)
                reasons = ca.check_compatibility(info, mm_image)
                if reasons:
                    raise ValueError(" ".join(reasons))
                corrected = ca.apply_correction(mm_image, path)

                parent = None
                if dataset_ids and dataset_ids.get(int(image_id)) is not None:
                    parent = conn.getObject(
                        "Dataset", int(dataset_ids[int(image_id)])
                    )
                if parent is None:
                    parent = img.getParent()
                new_name = chromatic_shift.aligned_image_name(name)
                new_image = omero_tools.create_image_from_numpy_array(
                    conn=conn,
                    # TZYXC -> zctyx (OMERO order)
                    data=corrected.transpose((1, 4, 0, 2, 3)),
                    image_name=new_name,
                    image_description=(
                        f"Chromagnon correction '{correction_name}' "
                        f"(FileAnnotation {ann_id}) applied to Image {image_id} "
                        f"'{name}'."
                    ),
                    dataset=parent,
                    source_image_id=image_id,
                )
                say(f"  -> {new_name} (Image {new_image.getId()})")
                results.append(
                    {
                        "image_id": image_id,
                        "name": name,
                        "ok": True,
                        "message": "",
                        "new_image_id": new_image.getId(),
                        "new_name": new_name,
                        "dataset_id": parent.getId() if parent else None,
                    }
                )
            except Exception as e:
                logger.exception(f"Could not correct image {image_id}")
                say(f"  !! {e}")
                results.append(
                    {"image_id": image_id, "name": name, "ok": False,
                     "message": str(e)}
                )
    finally:
        chromatic_shift.set_echo_func(None)
    return results
