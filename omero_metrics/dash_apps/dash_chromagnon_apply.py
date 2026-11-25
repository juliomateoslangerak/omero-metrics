"""Center panel "Chromagnon": apply a saved Chromagnon correction (Phase 2).

Shown by the "Chromagnon" center plugin when a dataset or one or more images
are selected in the webclient tree (see
``templates/omero_metrics/webclient_plugins/center_plugin.chromagnon.js.html``).

1. Choose a correction file (saved by the chromatic-shift analysis, or a
   ``*.chromagnon.csv`` / ``*.chromagnon.tif`` attached by hand).
2. The images of the selection are checked against it: an image is corrected
   only when all its channel wavelengths match those of the correction, and,
   for a local correction, its YX size matches the distortion map.
3. "Apply correction" creates ``<root>_ALN.tif`` next to each source image.
   Progress is streamed like the analysis form does (file log + clientside
   fetch), and the webclient tree is refreshed afterwards.
"""

import traceback

import dash
import dash_mantine_components as dmc
from dash import dcc, html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics import views
from omero_metrics.styles import CONTAINER_STYLE, MANTINE_THEME, THEME
from omero_metrics.tools import chromagnon_apply

dashboard_name = "omero_chromagnon_apply"
dash_chromagnon_apply = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=["/static/omero_metrics/css/style_app.css"],
)


def _section(title, description, children):
    return dmc.Paper(
        withBorder=True,
        radius="md",
        p="md",
        mb="md",
        children=[
            dmc.Title(title, order=4),
            dmc.Text(description, c="dimmed", size="sm", mb="sm"),
            *children,
        ],
    )


dash_chromagnon_apply.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        my_components.header_component(
            "Chromagnon Correction",
            "Apply a saved Chromagnon correction to images",
            "Chromagnon",
            load_buttons=False,
        ),
        dmc.Container(
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
            children=[
                html.Div(id="cg-blank"),
                html.Div(id="cg-load-error"),
                dcc.Store(id="cg-targets-store"),
                dcc.Store(id="cg-reasons-store"),
                dcc.Store(id="cg-key-store"),
                dcc.Store(id="cg-done-store"),
                html.Div(id="cg-refresh-dummy", style={"display": "none"}),
                dcc.Interval(
                    id="cg-progress-interval",
                    interval=1000,
                    n_intervals=0,
                    disabled=True,
                ),
                _section(
                    "1. Correction file",
                    "Correction files saved by the Chromatic Shift analysis, and "
                    "*.chromagnon.csv / *.chromagnon.tif files attached in this "
                    "group.",
                    [
                        dmc.Select(
                            id="cg-correction-select",
                            data=[],
                            placeholder="Select a correction file",
                            searchable=True,
                            nothingFoundMessage="No correction file found",
                            leftSection=my_components.get_icon(
                                icon="mdi:file-cog-outline"
                            ),
                        ),
                        dmc.Text(id="cg-correction-info", size="sm", mt="xs"),
                    ],
                ),
                _section(
                    "2. Images",
                    "The correction is applied only when all channel wavelengths "
                    "match, and, for a local correction, the YX size matches.",
                    [
                        html.Div(id="cg-targets-table"),
                        dmc.MultiSelect(
                            id="cg-target-select",
                            label="Images to correct",
                            data=[],
                            value=[],
                            searchable=True,
                            clearable=True,
                            mt="sm",
                        ),
                    ],
                ),
                dmc.Group(
                    justify="flex-end",
                    mb="md",
                    children=[
                        dmc.Button(
                            "Apply correction",
                            id="cg-apply-button",
                            color=THEME["primary"],
                            disabled=True,
                            leftSection=my_components.get_icon(icon="mdi:auto-fix"),
                        )
                    ],
                ),
                dmc.Paper(
                    id="cg-progress-panel",
                    withBorder=True,
                    radius="md",
                    p="md",
                    mb="md",
                    style={"display": "none"},
                    children=[
                        dmc.Group(
                            [dmc.Loader(size="sm"), dmc.Text("Progress", fw=500)],
                            gap="xs",
                            mb="xs",
                        ),
                        html.Pre(
                            id="cg-progress-log",
                            style={
                                "maxHeight": "260px",
                                "overflowY": "auto",
                                "whiteSpace": "pre-wrap",
                                "fontSize": "12px",
                                "margin": 0,
                                "fontFamily": "monospace",
                            },
                        ),
                    ],
                ),
                html.Div(id="cg-result"),
            ],
        ),
    ],
)


def _context(kwargs):
    return kwargs["session_state"].get("chromagnon_apply") or {}


def _error(msg, details=None):
    return dmc.Alert(
        [dmc.Text(msg, size="sm")]
        + ([dmc.Code(details, block=True)] if details else []),
        title="Error",
        color="red",
    )


def _shape_text(shape):
    t, z, y, x, c = shape
    text = f"{c}ch, Z{z}, {y}x{x}"
    return text + (f", T{t}" if t and t > 1 else "")


@dash_chromagnon_apply.expanded_callback(
    dash.dependencies.Output("cg-correction-select", "data"),
    dash.dependencies.Output("cg-targets-store", "data"),
    dash.dependencies.Output("cg-key-store", "data"),
    dash.dependencies.Output("cg-load-error", "children"),
    [dash.dependencies.Input("cg-blank", "children")],
)
def load_options(_, **kwargs):
    ctx = _context(kwargs)
    try:
        files, targets = views.chromagnon_apply_options(
            kwargs["request"], obj_type=ctx["obj_type"], ids=ctx["ids"]
        )
    except Exception as e:
        return [], [], None, _error(str(e), traceback.format_exc())
    options = [
        {"value": str(f["id"]), "label": chromagnon_apply.correction_option_label(f)}
        for f in files
    ]
    return options, targets, ctx.get("progress_key"), ""


# The table is rendered by this callback only. Server-side callbacks with
# allow_duplicate outputs are not applied under django-plotly-dash (the "@..."
# suffixed output ids are dropped), so each output has a single writer here.
@dash_chromagnon_apply.expanded_callback(
    dash.dependencies.Output("cg-targets-table", "children"),
    [
        dash.dependencies.Input("cg-targets-store", "data"),
        dash.dependencies.Input("cg-reasons-store", "data"),
    ],
)
def render_targets(targets, reasons, **kwargs):
    if targets is None:
        return dmc.Text("Loading images...", c="dimmed", size="sm")
    return _targets_table(targets, reasons)


def _targets_table(targets, reasons):
    if not targets:
        return dmc.Text("No images in the selection.", c="dimmed", size="sm")
    body = []
    for t in targets:
        if reasons is None:
            status = dmc.Text("—", c="dimmed", size="sm")
        elif reasons.get(str(t["id"])):
            status = dmc.Tooltip(
                label=" ".join(reasons[str(t["id"])]),
                multiline=True,
                w=360,
                children=dmc.Badge("not applicable", color="red", variant="light"),
            )
        else:
            status = dmc.Badge("OK", color="green", variant="light")
        body.append(
            dmc.TableTr(
                [
                    dmc.TableTd(t["name"]),
                    dmc.TableTd(str(t["waves"])),
                    dmc.TableTd(_shape_text(t["shape"])),
                    dmc.TableTd(status),
                ]
            )
        )
    # Built from TableTr/TableTd: dmc.Table(data=...) does not render components
    # in "body" (only head/foot are declared as component props in dmc 2.x), and
    # the React error blanks the whole app.
    head = dmc.TableThead(
        dmc.TableTr(
            [dmc.TableTh(h) for h in ("Image", "Wavelengths", "Size", "Status")]
        )
    )
    table = dmc.Table(
        [head, dmc.TableTbody(body)],
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
    )
    if reasons:
        notes = [
            dmc.ListItem(f"{t['name']}: {' '.join(reasons[str(t['id'])])}")
            for t in targets
            if reasons.get(str(t["id"]))
        ]
        if notes:
            return html.Div(
                [table, dmc.List(notes, size="sm", c="red", mt="xs")]
            )
    return table


@dash_chromagnon_apply.expanded_callback(
    dash.dependencies.Output("cg-correction-info", "children"),
    dash.dependencies.Output("cg-reasons-store", "data"),
    dash.dependencies.Output("cg-target-select", "data"),
    dash.dependencies.Output("cg-target-select", "value"),
    [
        dash.dependencies.Input("cg-correction-select", "value"),
        dash.dependencies.State("cg-targets-store", "data"),
    ],
    prevent_initial_call=True,
)
def check_correction(ann_id, targets, **kwargs):
    targets = targets or []
    if not ann_id:
        return "", None, [], []
    try:
        info, reasons = views.chromagnon_apply_check(
            kwargs["request"], ann_id=int(ann_id), targets=targets
        )
    except Exception as e:
        return _error(str(e), traceback.format_exc()), None, [], []
    reasons = {str(k): v for k, v in reasons.items()}
    ok = [t for t in targets if not reasons.get(str(t["id"]))]
    data = [{"value": str(t["id"]), "label": t["name"]} for t in ok]
    value = [str(t["id"]) for t in ok if t["default"]]
    info_text = chromagnon_apply.ca.correction_label(info)
    return info_text, reasons, data, value


@dash_chromagnon_apply.expanded_callback(
    dash.dependencies.Output("cg-apply-button", "disabled"),
    [
        dash.dependencies.Input("cg-correction-select", "value"),
        dash.dependencies.Input("cg-target-select", "value"),
    ],
)
def toggle_apply(ann_id, image_ids, **kwargs):
    return not (ann_id and image_ids)


@dash_chromagnon_apply.expanded_callback(
    dash.dependencies.Output("cg-result", "children"),
    dash.dependencies.Output("cg-apply-button", "loading"),
    dash.dependencies.Output("cg-done-store", "data"),
    [
        dash.dependencies.Input("cg-apply-button", "n_clicks"),
        dash.dependencies.State("cg-correction-select", "value"),
        dash.dependencies.State("cg-target-select", "value"),
        dash.dependencies.State("cg-key-store", "data"),
        dash.dependencies.State("cg-targets-store", "data"),
    ],
    prevent_initial_call=True,
)
def apply_correction(n_clicks, ann_id, image_ids, key, targets, **kwargs):
    if not (n_clicks and ann_id and image_ids):
        return dash.no_update, False, dash.no_update
    try:
        results = views.chromagnon_apply_run(
            kwargs["request"],
            ann_id=int(ann_id),
            image_ids=[int(i) for i in image_ids],
            progress_key=key,
            # Create each corrected image in the dataset it was listed from.
            dataset_ids={int(t["id"]): t.get("dataset_id") for t in targets or []},
        )
    except Exception as e:
        return _error(str(e), traceback.format_exc()), False, {"datasets": []}

    n_ok = sum(r["ok"] for r in results)
    items = []
    for r in results:
        if r["ok"]:
            items.append(
                dmc.ListItem(f"{r['name']} → {r['new_name']} (Image {r['new_image_id']})")
            )
        else:
            items.append(
                dmc.ListItem(dmc.Text(f"{r['name']}: {r['message']}", c="red", size="sm"))
            )
    color = "green" if n_ok == len(results) else ("orange" if n_ok else "red")
    alert = dmc.Alert(
        dmc.List(items, size="sm"),
        title=f"{n_ok} of {len(results)} images corrected",
        color=color,
    )
    datasets = sorted({r["dataset_id"] for r in results if r.get("dataset_id")})
    return alert, False, {"datasets": datasets}


# Show the progress panel and start polling when Apply is clicked.
dash_chromagnon_apply.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) { return window.dash_clientside.no_update; }
        return [false, {display: 'block'}, true, ""];
    }
    """,
    dash.dependencies.Output("cg-progress-interval", "disabled"),
    dash.dependencies.Output("cg-progress-panel", "style"),
    dash.dependencies.Output("cg-apply-button", "loading", allow_duplicate=True),
    dash.dependencies.Output("cg-result", "children", allow_duplicate=True),
    dash.dependencies.Input("cg-apply-button", "n_clicks"),
    prevent_initial_call=True,
)

# Poll the progress log through a plain Django view (not a Dash callback, which
# would be serialised behind the blocking apply in the same session).
dash_chromagnon_apply.clientside_callback(
    """
    async function(n, key) {
        if (!key) { return window.dash_clientside.no_update; }
        try {
            const r = await fetch("/omero_metrics/chromagnon/progress/" + key + "/",
                                  {credentials: "same-origin"});
            if (!r.ok) { return window.dash_clientside.no_update; }
            const text = await r.text();
            requestAnimationFrame(function() {
                const el = document.getElementById("cg-progress-log");
                if (el) { el.scrollTop = el.scrollHeight; }
            });
            return text;
        } catch (e) {
            return window.dash_clientside.no_update;
        }
    }
    """,
    dash.dependencies.Output("cg-progress-log", "children"),
    dash.dependencies.Input("cg-progress-interval", "n_intervals"),
    dash.dependencies.State("cg-key-store", "data"),
)

# When done: stop polling, hide the panel and refresh the dataset nodes of the
# webclient tree so the new <root>_ALN.tif images appear. The panel itself is
# not reloaded, so the result stays visible.
dash_chromagnon_apply.clientside_callback(
    """
    function(data) {
        if (!data) { return window.dash_clientside.no_update; }
        try {
            var p = window.parent;
            if (p && p !== window && p.$ && p.$.jstree) {
                var inst = p.$.jstree.reference("#dataTree");
                (data.datasets || []).forEach(function (id) {
                    var node = inst && inst.locate_node("dataset-" + id)[0];
                    if (node) { inst.refresh_node(node); }
                });
            }
        } catch (e) {
            console.error("tree refresh failed", e);
        }
        return [true, {display: 'none'}, ""];
    }
    """,
    dash.dependencies.Output("cg-progress-interval", "disabled", allow_duplicate=True),
    dash.dependencies.Output("cg-progress-panel", "style", allow_duplicate=True),
    dash.dependencies.Output("cg-refresh-dummy", "children"),
    dash.dependencies.Input("cg-done-store", "data"),
    prevent_initial_call=True,
)
