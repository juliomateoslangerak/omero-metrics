"""Dropdown choices for analysis-parameter form fields.

The forms are generated from the schema (dash_forms_tools.render_fieldset); a
field listed here is shown as a dropdown instead of a number input.

``reference_channel_index`` (Chromatic Shift) is set in the project
configuration, before the images of an analysis are chosen, so the choices are
the channels of the images in the project, labelled with their emission
wavelengths: "Auto", "0 — 528 nm", "1 — 609 nm". When the images differ, the
wavelengths are listed together ("0 — 525 / 528 nm").
"""

import logging

from omero.gateway import BlitzGateway

from omero_metrics.tools.chromagnon_correction import is_output_name

logger = logging.getLogger(__name__)

# Do not read the channels of more images than this for one form.
MAX_IMAGES = 500


def _channel_labels(conn: BlitzGateway, project_id: int) -> list:
    """For each channel index: the set of wavelengths (or names) in the project."""
    project = conn.getObject("Project", int(project_id))
    if project is None:
        return []
    labels = []  # index -> set of str
    n_images = 0
    for dataset in project.listChildren():
        for image in dataset.listChildren():
            if is_output_name(image.getName()):
                # Outputs of the chromatic shift analysis (e.g. the 1-channel
                # distortion magnitude images) are not analysis inputs.
                continue
            n_images += 1
            if n_images > MAX_IMAGES:
                return labels
            try:
                channels = image.getChannels(noRE=True) or []
            except Exception:
                logger.exception(
                    f"Could not read the channels of image {image.getId()}"
                )
                continue
            for i, ch in enumerate(channels):
                while len(labels) <= i:
                    labels.append(set())
                wave = ch.getEmissionWave()
                if wave:
                    labels[i].add(f"{int(round(float(wave)))} nm")
                elif ch.getLabel():
                    labels[i].add(ch.getLabel())
    return labels


def _sort_key(text):
    number = text.split(" ")[0]
    return (0, float(number)) if number.replace(".", "").isdigit() else (1, text)


def reference_channel_options(conn: BlitzGateway, project_id: int) -> list:
    """Choices for reference_channel_index, or [] when the project has no images."""
    labels = _channel_labels(conn, project_id)
    if not labels:
        return []
    options = [{"value": "-1", "label": "Auto (from wavelength and intensity)"}]
    for i, names in enumerate(labels):
        names = sorted(names, key=_sort_key)
        if not names:
            text = f"{i}"
        elif all(n.endswith(" nm") for n in names):
            text = f"{i} — " + " / ".join(n[:-3] for n in names) + " nm"
        else:
            text = f"{i} — " + " / ".join(names)
        options.append({"value": str(i), "label": text})
    return options


def field_options(conn: BlitzGateway, project_id) -> dict:
    """Dropdown choices for the parameter forms of a project."""
    if project_id is None:
        return {}
    try:
        options = reference_channel_options(conn, project_id)
    except Exception:
        logger.exception(f"Could not list the channels of project {project_id}")
        return {}
    return {"reference_channel_index": options} if options else {}
