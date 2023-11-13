from logging import Logger
import logging
from typing import Callable
from arches.app.models.resource import Resource

from arches.app.utils.search_thumbnail_fetcher import SearchThumbnailFetcher

logger = logging.getLogger(__name__)

class SearchThumbnailFetcherFactory(object):
    registry = {}

    @classmethod
    def register(cls, name:str):
        def inner_wrapper(wrapped_class: SearchThumbnailFetcher) -> Callable:
            if name in cls.registry:
                logger.warning('Search Thumbnail Fetcher %s already exists. Will replace it', name)
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create_thumbnail_fetcher(cls, resource_id: str, **kwargs) -> SearchThumbnailFetcher:
        """ Factory command to create the template engine """
        resource = Resource.objects.get(resourceinstanceid=resource_id)
        try:
            search_thumbnail_fetcher_class = cls.registry[str(resource.graph_id)]
            search_thumbnail_fetcher = search_thumbnail_fetcher_class(resource, **kwargs)
            return search_thumbnail_fetcher
        except KeyError:
            pass # there is no thumbnail fetcher registered for the graph requested

        try:
            search_thumbnail_fetcher_class = cls.registry['default']
            search_thumbnail_fetcher = search_thumbnail_fetcher_class(resource, **kwargs)
            return search_thumbnail_fetcher
        except KeyError:
            return None # there is no default thumbnail fetcher registered, return false.