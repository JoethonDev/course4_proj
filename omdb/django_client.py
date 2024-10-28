from django.conf import settings

from omdb.client import OMDbClient


def get_client_from_settings():
    """Create an instance of an OmdbClient using the OMDB_KEY from the Django settings."""
    return OMDbClient(settings.OMDB_KEY)