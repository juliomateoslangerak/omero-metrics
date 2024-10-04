set -eu

export PATH="/opt/omero/web/venv3/bin:$PATH"
python=/opt/omero/web/venv3/bin/python
cd /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb

echo "Run migrate to update the database OMERO.web"
exec $python manage.py migrate