#!/usr/bin/env bash

# Usage: ./configuration_omero.sh [OMEROWEB_PATH]
# This script configures OMERO.web with the specified paths and settings.
# If OMEROWEB_PATH is not provided, it will be auto-detected from the active environment.

set -e

# Auto-detect OMEROWEB_PATH if not provided
if [ "$#" -eq 0 ]; then
    # Try to find omeroweb in the current Python environment
    OMEROWEB_PATH=$(python -c "import sys; import os; import omeroweb; print(os.path.dirname(omeroweb.__file__))" 2>/dev/null)
    if [ -z "$OMEROWEB_PATH" ]; then
        echo "Error: Could not auto-detect OMEROWEB_PATH. Please activate your virtual environment before running this script or provide it as an argument."
        echo "Usage: $0 [OMEROWEB_PATH]"
        exit 1
    fi
    echo "Auto-detected OMEROWEB_PATH: $OMEROWEB_PATH"
elif [ "$#" -eq 1 ]; then
    OMEROWEB_PATH="$1"
else
    echo "Usage: $0 [OMEROWEB_PATH]"
    echo "  OMEROWEB_PATH: Optional, will be auto-detected from active Python environment if not provided"
    exit 1
fi

# Set required environment variable
mkdir "omerodir"
export OMERODIR="$(pwd)/omerodir"

# Append required apps
omero config append omero.web.apps '"omero_metrics"'
omero config append omero.web.apps '"dpd_static_support"'
omero config append omero.web.apps '"django_plotly_dash"'
omero config append omero.web.apps '"bootstrap4"'
omero config append omero.web.apps '"corsheaders"'

# Configure top links
omero config append omero.web.ui.top_links '["Metrics", "omero_metrics_index", {"title": "Open app in new tab", "target": "_blank"}]'

# Center plugins
omero config append omero.web.ui.center_plugins '["Metrics View", "omero_metrics/webclient_plugins/center_plugin.metricsview.js.html", "metrics_view_panel"]'

# Set debug mode
omero config set omero.web.debug True

# Set secure mode
omero config set omero.web.secure True

# Set server list
# Modify if necessary to connect to your omero server. This configuration is to connect to the
# docker server created by the "docker compose up -d" command
omero config set omero.web.server_list '[["localhost", 6064, "omero"]]'

# Add middleware for CORS
omero config append omero.web.middleware '{"index": 0.5, "class": "corsheaders.middleware.CorsMiddleware"}'
omero config append omero.web.middleware '{"index": 10, "class": "corsheaders.middleware.CorsPostCsrfMiddleware"}'
omero config set omero.web.cors_origin_allow_all True

# Configure the database (SQLite)
# We are placing the database inside the OMERODIR path, but you may choose somewhere else.
omero config set omero.web.databases "{\"default\": {\"ENGINE\": \"django.db.backends.sqlite3\", \"NAME\": \"$OMERODIR/django_plotly_dash_db\"}}"

# Add django_plotly_dash and whitenoise middleware
omero config append omero.web.middleware '{"index": 7, "class": "django_plotly_dash.middleware.ExternalRedirectionMiddleware"}'
omero config append omero.web.middleware '{"index": 0.5, "class": "whitenoise.middleware.WhiteNoiseMiddleware"}'
omero config append omero.web.middleware '{"index": 8, "class": "django_plotly_dash.middleware.BaseMiddleware"}'

# omero_metrics middleware
omero config append omero.web.middleware '{"index":0.1, "class": "omero_metrics.middleware.OmeroAuth"}'

# Run migrations
python "$OMEROWEB_PATH/manage.py" migrate

echo "OMERO.web configuration complete."
