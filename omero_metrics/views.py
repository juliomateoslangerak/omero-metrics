import inspect
import logging
import traceback

import numpy as np
import omero
from django.http import HttpResponse
from django.shortcuts import render
from microscopemetrics import AnalysisError, SaturationError
from microscopemetrics_schema import datamodel as mm_schema
from omero.gateway import FileAnnotationWrapper
from omeroweb.webclient.decorators import login_required

from omero_metrics.tools import (
    chromagnon_apply,
    chromagnon_correction,
    data_managers,
    delete,
    dump,
    form_options,
    load,
    namespaces,
    omero_tools,
    progress,
    schema_utils,
)

logger = logging.getLogger(__name__)


TEMPLATE_DASH_NAME = "omero_metrics/dash_template_center_ui/dash_template.html"


@login_required()
def dataset_analysis_progress(request, dataset_id, conn=None, **kwargs):
    """Live progress log of the analysis running on ``dataset_id`` (plain text).

    A plain Django view rather than a Dash callback: while the blocking analysis
    callback runs, other callbacks of the same django-plotly-dash session wait
    behind it, so the browser polls this view instead (see dataset_form).
    """
    return HttpResponse(progress.read(dataset_id), content_type="text/plain")


@login_required(setGroupContext=True)
def image_planes(request, conn=None, **kwargs):
    """Planes ``(z, c, t=0)`` of image ``image_id`` for ``channels`` (2D arrays).

    Used by dashboards that show one Z section at a time, so that the whole
    stack is not kept in the session.
    """
    image = conn.getObject("Image", int(kwargs["image_id"]))
    if image is None:
        raise ValueError(f"Image {kwargs['image_id']} was not found.")
    z = int(min(max(int(kwargs["z"]), 0), image.getSizeZ() - 1))
    pixels = image.getPrimaryPixels()
    return list(pixels.getPlanes([(z, int(c), 0) for c in kwargs["channels"]]))


@login_required(setGroupContext=True)
def corrected_section(request, conn=None, **kwargs):
    """Section ``z`` of image ``image_id`` corrected for display with the
    correction file ``ann_id``; returns the planes of ``channels`` (2D arrays).

    Only the planes that the correction maps to ``z`` are read, and only the
    in-plane part is resampled (microscopemetrics chromagnon_apply).
    """
    from microscopemetrics.analyses import chromagnon_apply

    image = conn.getObject("Image", int(kwargs["image_id"]))
    if image is None:
        raise ValueError(f"Image {kwargs['image_id']} was not found.")
    path = chromagnon_correction.download_correction(conn, int(kwargs["ann_id"]))
    mm_image = load.load_image(image, load_array=False)
    sources = chromagnon_apply.section_sources(mm_image, path, int(kwargs["z"]))
    pixels = image.getPrimaryPixels()
    planes = np.stack(
        list(pixels.getPlanes([(z, c, 0) for c, z in enumerate(sources)]))
    )
    section = chromagnon_apply.correct_section(mm_image, planes, path)
    return [section[int(c)] for c in kwargs["channels"]]


@login_required()
def chromagnon_apply_progress(request, key, conn=None, **kwargs):
    """Live progress log of a running "apply Chromagnon correction" job."""
    return HttpResponse(progress.read(key), content_type="text/plain")


@login_required(setGroupContext=True)
def chromagnon_apply_view(request, conn=None, **kwargs):
    """Center panel: apply a saved Chromagnon correction to images.

    ``?dataset=<id>`` (one dataset) or ``?image=<id>,<id>,...`` (images).
    """
    dash_context = request.session.get("django_plotly_dash", {})
    try:
        if request.GET.get("dataset"):
            obj_type, ids = "dataset", [int(request.GET["dataset"])]
        elif request.GET.get("image"):
            obj_type = "image"
            ids = [int(i) for i in request.GET["image"].split(",") if i]
        else:
            raise ValueError("Select a dataset or one or more images.")
        # A separate key, so that it does not clash with the Metrics View context.
        dash_context["chromagnon_apply"] = {
            "obj_type": obj_type,
            "ids": ids,
            "progress_key": f"apply_{obj_type}_{ids[0]}",
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "omero_chromagnon_apply"},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def chromagnon_apply_options(request, conn=None, **kwargs):
    """Correction files of the group and the target images (for the Dash app)."""
    files = chromagnon_apply.list_correction_files(conn)
    targets = chromagnon_apply.list_target_images(
        conn, kwargs["obj_type"], kwargs["ids"]
    )
    return files, targets


@login_required(setGroupContext=True)
def chromagnon_apply_check(request, conn=None, **kwargs):
    """Header of correction ``ann_id`` and which targets it can be applied to."""
    path = chromagnon_correction.download_correction(conn, kwargs["ann_id"])
    info = chromagnon_apply.ca.read_correction_info(path)
    reasons = chromagnon_apply.check_targets(conn, info, kwargs["targets"])
    return info, reasons


@login_required(setGroupContext=True)
def chromagnon_apply_run(request, conn=None, **kwargs):
    """Apply correction ``ann_id`` to ``image_ids``; progress goes to ``progress_key``."""
    key = kwargs["progress_key"]
    progress.clear(key)
    return chromagnon_apply.apply_to_images(
        conn,
        kwargs["ann_id"],
        kwargs["image_ids"],
        echo=progress.make_echo_func(key),
        dataset_ids=kwargs.get("dataset_ids"),
    )


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "omero_metrics/top_link_template/index.html", context)


@login_required(setGroupContext=True)
def center_viewer_image(request, image_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        image_wrapper = conn.getObject("Image", image_id)
        im = data_managers.ImageManager(conn, image_wrapper)
        im.load_context()
        dash_context["context"] = im.context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": im.app_name},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_project(request, project_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        project_wrapper = conn.getObject("Project", project_id)
        pm = data_managers.ProjectManager(conn, project_wrapper)
        pm.load_context()
        if pm.input_parameters is None:
            # No analyzed datasets or input parameters so we need to trigger
            # the configuration form
            dash_context["context"] = {"project_id": project_id}
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "omero_project_config_form"},
            )
        if pm.mm_dataset_collection:  # There is at least one analyzed dataset
            if pm.is_harmonized():
                dash_context["context"] = pm.context
                request.session["django_plotly_dash"] = dash_context
                return render(
                    request,
                    template_name=TEMPLATE_DASH_NAME,
                    context={"app_name": "omero_project_dash"},
                )
            else:
                dash_context["context"] = {
                    "message": "OMERO-metrics does not support non-harmonized projects."
                }
                request.session["django_plotly_dash"] = dash_context
                return render(
                    request,
                    template_name=TEMPLATE_DASH_NAME,
                    context={"app_name": "WarningApp"},
                )
        else:  # No analyzed datasets but input parameters configured
            dash_context["context"] = pm.context
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "omero_project_dash"},
            )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_group(request, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())

    try:
        if request.session.get("active_group"):
            active_group_id = request.session["active_group"]
        else:
            active_group_id = conn.getEventContext().groupId
        active_group_wrapper = conn.getObject("ExperimenterGroup", active_group_id)
        gm = data_managers.ExperimenterGroupManager(conn, active_group_wrapper)
        gm.load_context()
        if not gm.mm_dataset_collections:
            dash_context["context"] = {
                "message": "This group does not have any analysis."
            }
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "WarningApp"},
            )
        else:
            dash_context["context"] = gm.context
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "omero_group_dash"},
            )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_dataset(request, dataset_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", {})
    try:
        dataset_wrapper = conn.getObject("Dataset", dataset_id)
        dm = data_managers.DatasetManager(conn, dataset_wrapper)
        dm.load_context()
        dash_context["context"] = dm.context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": dm.app_name},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def microscope_view(request, conn=None, **kwargs):
    """This is to display the microscope dashboard
    for the top link ui"""
    return render(
        request,
        template_name="omero_metrics/top_link_template/microscope.html",
        context={"app_name": "top_iu_microscope"},
    )


@login_required(setGroupContext=True)
def center_view_projects(request, conn=None, **kwargs):
    """This is to display the project dashboard
    for the top link ui"""
    id_list = request.GET.get("projectIds", None)
    id_list = request.GET.get("Project", id_list)
    dash_context = request.session.get("django_plotly_dash", {})
    if not id_list:
        # Not really sure when this could happen
        dash_context["context"] = {"message": "No project ids provided."}
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "WarningApp"},
        )
    try:
        project_ids = [int(i) for i in id_list.split(",")]
        data = {}
        for project_id in project_ids:
            project_wrapper = conn.getObject("Project", project_id)
            pm = data_managers.ProjectManager(conn, project_wrapper)
            pm.load_context()
            if pm.input_parameters and pm.is_harmonized():
                dash_context["context"][f"{project_id}"] = pm.context

        if not dash_context["context"]:
            dash_context["context"] = {
                "message": "OMERO-metrics did not detect any analyzed projects in the selection."
            }
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "WarningApp"},
            )

        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "omero_multiple_projects"},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


# These views are called from the dash app, and they return a message and a color to display in the app.


@login_required(setGroupContext=True)
def save_config(request, conn=None, **kwargs):
    """Save the configuration file"""
    # TODO: We must split study_config into the different components
    try:
        project_id = kwargs["project_id"]
        mm_input_parameters = kwargs["input_parameters"]
        mm_sample = kwargs["sample"]
        project_wrapper = conn.getObject("Project", project_id)
        setup = load.load_input_config_file(project_wrapper)
        try:
            if setup:
                to_delete = []
                for ann in project_wrapper.listAnnotations():
                    if isinstance(ann, FileAnnotationWrapper):
                        ns = ann.getNs()
                        if (
                            ns
                            in namespaces.LIST_NS_MICROSCOPEMETRICS_SCHEMA_INPUT_PARAMETERS
                        ):
                            to_delete.append(ann.getId())
                if to_delete:
                    # TODO: call omero_tools
                    # TODO: make deletions more specific
                    conn.deleteObjects(
                        graph_spec="Annotation",
                        obj_ids=to_delete,
                        deleteAnns=True,
                        deleteChildren=True,
                        wait=True,
                    )
            dump.dump_config_input_parameters(
                conn,
                project_wrapper,
                mm_input_parameters,
                mm_sample,
            )
            return (
                "success",
                "Configuration saved successfully. Select the project to see the changes.",
            )
        except omero.SecurityViolation:
            return (
                "authorisation_error",
                "You don't have the necessary permissions to save the configuration.",
            )
        except Exception as e:
            return "unidentified_error", str(e)
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def run_analysis_view(request, conn=None, **kwargs):
    """Run the analysis"""
    try:
        dataset_wrapper = conn.getObject("Dataset", kwargs["dataset_id"])
        project_wrapper = dataset_wrapper.getParent()
        list_images = kwargs["list_images"]
        comment = kwargs["comment"]
        list_mm_images = [
            load.load_image(conn.getObject("Image", int(i))) for i in list_images
        ]
        acquisition_datetime = sorted(
            [i.acquisition_datetime for i in list_mm_images]
        )[-1]
        mm_sample = kwargs["mm_sample"]
        mm_input_parameters = kwargs["mm_input_parameters"]
        dataset_class = schema_utils.get_dataset_class(mm_input_parameters.__class__)
        input_data_class = schema_utils.get_input_data_class(dataset_class)
        images_field = schema_utils.get_image_fields(dataset_class)["input_data"][0]
        input_data = input_data_class(**{images_field: list_mm_images})
        mm_microscope = mm_schema.Microscope(
            name=project_wrapper.getDetails().getGroup().getName()
        )
        mm_experimenter = mm_schema.Experimenter(
            # TODO: we must get the ORCID from somewhere here
            orcid="0000-0002-1825-0097",
            name=conn.getUser().getName(),
        )
        mm_dataset = dataset_class(
            name=dataset_wrapper.getName(),
            description=dataset_wrapper.getDescription(),
            data_reference=omero_tools.get_ref_from_object(dataset_wrapper),
            input_parameters=mm_input_parameters,
            microscope=mm_microscope,
            sample=mm_sample,
            input_data=input_data,
            acquisition_datetime=acquisition_datetime,
            experimenter=mm_experimenter,
        )
        analysis_function = schema_utils.get_analysis_function(dataset_class)
        # Analyses that report progress (the chromatic shift analysis forwards
        # Chromagnon's messages) expose set_echo_func: the messages go to a
        # per-dataset log that the form polls (dataset_analysis_progress).
        analysis_module = inspect.getmodule(analysis_function)
        set_echo_func = getattr(analysis_module, "set_echo_func", None)
        if set_echo_func is not None:
            progress.clear(kwargs["dataset_id"])
            set_echo_func(progress.make_echo_func(kwargs["dataset_id"]))
        try:
            # Run the analysis
            analysis_function(mm_dataset)
        except AnalysisError or SaturationError as e:
            logger.error(f"{e}")
            return "analysis_error", str(e), e.suggestion
        except Exception as e:
            logger.error(f"Error running the analysis: {e}")
            return (
                "unidentified_error",
                "Error during analysis run:\n"
                f"{e}\n"
                "Please, contact support with the following traceback:",
                traceback.format_exc(),
            )
        finally:
            if set_echo_func is not None:
                set_echo_func(None)
        if mm_dataset.processed:
            try:
                if comment:
                    mm_comment = mm_schema.Comment(
                        comment_datetime=acquisition_datetime,
                        text=comment,
                        comment_type="PROCESSING",
                    )
                    mm_dataset["output"]["comment"] = mm_comment
                dump.dump_dataset(
                    conn=conn,
                    dataset=mm_dataset,
                    target_project=project_wrapper,
                    dump_as_project_file_annotation=True,
                    dump_as_dataset_file_annotation=True,
                    dump_input_images=False,
                    dump_analysis=True,
                )

                logger.info(f"Analysis completed successfully")
                return (
                    "success",
                    "Analysis completed successfully.",
                    mm_dataset.description,
                )
            except Exception as e:
                logger.error(f"Error saving the analysis: {e}")
                return (
                    "unidentified_error",
                    "Error while saving the analysis.\n"
                    f"{e}\n"
                    "Please, contact support with the following traceback:",
                    traceback.format_exc(),
                )
        else:
            logger.error("Analysis run but dataset.processed is False.")
            return (
                "unidentified_error",
                "Analysis run but something prevented it to be tagged as processed.\n"
                "Please, contact support with the following traceback:",
                traceback.format_exc(),
            )
    except Exception as e:
        logger.error(f"Error during run_analysis_view execution: {e}")
        return (
            "unidentified_error",
            "run_analysis_view could not proceed.\n"
            f"{e}\n"
            "Please, contact support with the following traceback:",
            traceback.format_exc(),
        )


@login_required(setGroupContext=True)
def delete_all(request, conn=None, **kwargs):
    """Delete all the files"""
    try:
        group_id = kwargs["group_id"]
        for project in conn.getObjects("Project", opts={"group": group_id}):
            pm = data_managers.ProjectManager(conn, project)
            pm.load_data()
            pm.delete_processed_data()
        return delete.delete_all_annotations(conn, group_id)
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def delete_dataset(request, conn=None, **kwargs):
    """Delete the dataset outputs"""
    dataset_id = kwargs["dataset_id"]
    logger.info(f"Deleting dataset {dataset_id}")
    dataset_wrapper = conn.getObject("Dataset", dataset_id)
    dm = data_managers.DatasetManager(conn, dataset_wrapper)
    dm.load_data(load_images=False)
    try:
        dm.delete_processed_data()
        return "success", "Output deleted successfully."
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def form_field_options(request, conn=None, **kwargs):
    """Dropdown choices for the parameter forms (see tools/form_options.py).

    Pass ``project_id``, or ``dataset_id`` to use the dataset's project.
    """
    project_id = kwargs.get("project_id")
    if project_id is None and kwargs.get("dataset_id") is not None:
        dataset = conn.getObject("Dataset", int(kwargs["dataset_id"]))
        parent = dataset.getParent() if dataset else None
        project_id = parent.getId() if parent else None
    return form_options.field_options(conn, project_id)


@login_required(setGroupContext=True)
def delete_project(request, conn=None, **kwargs):
    """Delete the project outputs"""
    project_id = kwargs["project_id"]
    logger.info(f"Deleting dataset {project_id}")
    project_wrapper = conn.getObject("Project", project_id)
    pm = data_managers.ProjectManager(conn, project_wrapper)
    pm.load_data()
    try:
        pm.delete_processed_data()
        return "success", "Output deleted successfully."
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def save_threshold(request, conn=None, **kwargs):
    """Save the threshold"""
    try:
        project_id = kwargs["project_id"]
        threshold = kwargs["threshold"]
        project_wrapper = conn.getObject("Project", project_id)
        threshold_exist = load.load_thresholds_file(project_wrapper)
        if threshold:
            if threshold_exist:
                to_delete = []
                for ann in project_wrapper.listAnnotations(
                    ns=namespaces.NS_THRESHOLDS
                ):
                    if isinstance(ann, FileAnnotationWrapper):
                        to_delete.append(ann.getId())
                conn.deleteObjects(
                    graph_spec="Annotation",
                    obj_ids=to_delete,
                    deleteAnns=True,
                    deleteChildren=True,
                    wait=True,
                )
            dump.dump_threshold(conn, project_wrapper, threshold)
            return (
                "success",
                "Threshold saved successfully. Select the project to see the changes.",
            )
        else:
            return (
                "unidentified_error",
                "Failed to save threshold Configuration file doesn't exist.",
            )
    except Exception as e:
        if isinstance(e, omero.SecurityViolation):
            return (
                "authorisation_error",
                "You don't have the necessary permissions to save the threshold.",
            )
        elif isinstance(e, omero.CmdError):
            return (
                "unidentified_error",
                "You don't have the necessary permissions to save the threshold.",
            )
        else:
            return (
                "unidentified_error",
                "Something happened. Couldn't save thresholds.",
            )


@login_required(setGroupContext=True)
def imageJ(request, conn=None, **kwargs):
    """Run ImageJ"""
    return render(
        request,
        template_name="omero_metrics/top_link_template/imagej_template.html",
        context={"app_name": "imageJ"},
    )
