#!/usr/bin/env bash

# Usage: ./configuration_omero.sh /path/to/omeroweb /path/to/mydatabase
# This script configures OMERO.web with the specified paths and settings.

set -e

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <OMEROWEB_PATH> <DB_PATH>"
    exit 1
fi

OMEROWEB_PATH="$1"
DB_PATH="$2"

# Set required environment variable
export OMERODIR=$(pwd)

# Append required apps
omero config append omero.web.apps '"OMERO_metrics"'
omero config append omero.web.apps '"dpd_static_support"'
omero config append omero.web.apps '"django_plotly_dash"'
omero config append omero.web.apps '"bootstrap4"'
omero config append omero.web.apps '"corsheaders"'

# Configure top links
omero config append omero.web.ui.top_links '["Metrics", "OMERO_metrics_index", {"title": "Open app in new tab", "target": "_blank"}]'

# Set debug mode
omero config set omero.web.debug True

# Set secure mode
omero config set omero.web.secure True

# Set server list
omero config set omero.web.server_list '[["localhost", 4064, "omero"]]'

# Add middleware for CORS
omero config append omero.web.middleware '{"index": 0.5, "class": "corsheaders.middleware.CorsMiddleware"}'
omero config append omero.web.middleware '{"index": 10, "class": "corsheaders.middleware.CorsPostCsrfMiddleware"}'
omero config set omero.web.cors_origin_allow_all True

# Configure the database (SQLite)
# Ensure DB_PATH leads to a valid directory or filename as you intend.
omero config set omero.web.databases "{\"default\": {\"ENGINE\": \"django.db.backends.sqlite3\", \"NAME\": \"$DB_PATH/django_plotly_dash_db\"}}"

# Add django_plotly_dash and whitenoise middleware
omero config append omero.web.middleware '{"index": 7, "class": "django_plotly_dash.middleware.ExternalRedirectionMiddleware"}'
omero config append omero.web.middleware '{"index": 0.5, "class": "whitenoise.middleware.WhiteNoiseMiddleware"}'
omero config append omero.web.middleware '{"index": 8, "class": "django_plotly_dash.middleware.BaseMiddleware"}'

# OMERO_metrics middleware
omero config append omero.web.middleware '{"index":0.1, "class": "OMERO_metrics.middleware.OmeroAuth"}'

# Center plugins
omero config append omero.web.ui.center_plugins '["Metrics View", "OMERO_metrics/webclient_plugins/center_plugin.metricsview.js.html", "metrics_view_panel"]'

# Run migrations
python "$OMEROWEB_PATH/manage.py" migrate

echo "OMERO.web configuration complete."
