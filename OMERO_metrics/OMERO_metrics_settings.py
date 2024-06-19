import sys
from omeroweb.settings import process_custom_settings, report_settings


OMERO_METRICS_SETTINGS_MAPPING = {
    "omero.web.OMERO_metrics.top_links": [
        "TOP_LINKS",
        [["Metrics", "OMERO_metrics_index"]],
    ],
}


process_custom_settings("OMERO_metrics", "OMERO_METRICS_SETTINGS_MAPPING")
report_settings(sys.modules[__name__])
