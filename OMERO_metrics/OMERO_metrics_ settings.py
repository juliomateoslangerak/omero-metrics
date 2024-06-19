import json
import sys
from omeroweb.settings import process_custom_settings, report_settings

METRICS_SETTINGS_MAPPING = {
    "omero.web.OMERO_metrics.top_links": [
        "TOP_LINKS",
        (["metrics", "OMERO_metrics_index"]),
    ],
}

process_custom_settings(
    sys.modules[__name__], "OMERO_METRICS_SETTINGS_MAPPING"
)
report_settings(sys.modules[__name__])
