from django.conf import settings

settings.TOP_LINKS.append(["Metrics", "OMERO_metrics_index"])
settings.CENTER_PLUGINS.append(
    [
        "Metrics View",
        "OMERO_metrics_index/webclient_plugins/center_plugin.metricsview.js.html",
        "metrics_view_panel",
    ]
)
