from omeroweb.testlib import IWebTest, get
import pytest
from django.urls import reverse
from omero.gateway import BlitzGateway


def get_connection(user, group_id=None):
    """Get a BlitzGateway connection for the given user's client."""
    connection = BlitzGateway(client_obj=user[0])
    # Refresh the session context
    connection.getEventContext()
    if group_id is not None:
        connection.SERVICE_OPTS.setOmeroGroup(group_id)
    return connection


class TestLoadIndexPage(IWebTest):
    """Tests loading the index page."""

    @pytest.fixture()
    def user1(self):
        """Return a new user in a read-annotate group."""
        group = self.new_group(perms="rwra--")
        user = self.new_client_and_user(group=group)
        return user

    def test_load_index(self, user1):
        """Test loading the app home page."""
        conn = get_connection(user1)
        user_name = conn.getUser().getName()
        django_client = self.new_django_client(user_name, user_name)
        index_url = reverse("OMERO_metrics_index")
        # asserts we get a 200 response code etc
        rsp = get(django_client, index_url)
        html_str = rsp.content.decode()
        assert "Welcome" in html_str
