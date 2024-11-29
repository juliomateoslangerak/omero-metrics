from django.apps import AppConfig
from django.conf import settings
import logging


class OMEROMetricsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "OMERO_metrics"

    def ready(self):
        # Call functions to dynamically modify settings
        self.add_staticfiles_finders()
        self.add_plotly_components()
        self.add_plotly_dash_settings()
        self.add_context_processor()

    def add_staticfiles_finders(self):
        """Add custom static files finders for django-plotly-dash."""
        staticfiles_finders = [
            "django_plotly_dash.finders.DashAssetFinder",
            "django_plotly_dash.finders.DashComponentFinder",
            "django_plotly_dash.finders.DashAppDirectoryFinder",
        ]
        if hasattr(settings, "STATICFILES_FINDERS"):
            updated_finders = list(settings.STATICFILES_FINDERS)
            updated_finders.extend(
                f for f in staticfiles_finders if f not in updated_finders
            )
            settings.STATICFILES_FINDERS = tuple(updated_finders)
        else:
            settings.STATICFILES_FINDERS = tuple(staticfiles_finders)

    def add_plotly_components(self):
        """Add required Plotly Dash components."""
        plotly_components = [
            "dpd_components",
            "dash_bootstrap_components",
            "dash_iconify",
            "dash_mantine_components",
            "dpd_static_support",
        ]
        if hasattr(settings, "PLOTLY_COMPONENTS"):
            settings.PLOTLY_COMPONENTS.extend(
                c
                for c in plotly_components
                if c not in settings.PLOTLY_COMPONENTS
            )
        else:
            settings.PLOTLY_COMPONENTS = plotly_components

    def add_plotly_dash_settings(self):
        """Configure settings for django-plotly-dash."""
        plotly_dash_settings = {
            "ws_route": "dpd/ws/channel",
            "http_route": "dpd/views",
            "http_poke_enabled": True,
            "insert_demo_migrations": False,
            "cache_timeout_initial_arguments": 60,
            "view_decorator": None,
            "cache_arguments": False,
            "serve_locally": True,
        }
        if hasattr(settings, "PLOTLY_DASH"):
            settings.PLOTLY_DASH.update(plotly_dash_settings)
        else:
            settings.PLOTLY_DASH = plotly_dash_settings

    def add_context_processor(self):
        """Ensure the required context processor is included."""
        if hasattr(settings, "TEMPLATES") and len(settings.TEMPLATES) > 0:
            context_processors = (
                settings.TEMPLATES[0]
                .get("OPTIONS", {})
                .get("context_processors", [])
            )
            if (
                "django.template.context_processors.request"
                not in context_processors
            ):
                context_processors.append(
                    "django.template.context_processors.request"
                )
                settings.TEMPLATES[0]["OPTIONS"][
                    "context_processors"
                ] = context_processors
        else:
            logger = logging.getLogger(__name__)
            logger.error(
                "TEMPLATES setting is not properly configured. Unable to add context processor."
            )
