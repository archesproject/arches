from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound
from arches.app.utils.search_thumbnail_fetcher_factory import (
    SearchThumbnailFetcherFactory,
)


class ThumbnailView(View):
    def head(self, request, resource_id):
        fetcher = self.get_thumbnail_fetcher(resource_id)
        if fetcher is None:
            return HttpResponseNotFound()
        thumbnail = fetcher.get_thumbnail(False)
        if thumbnail is not None:
            return HttpResponse()
        else:
            return HttpResponseNotFound()

    def get(self, request, resource_id):
        fetcher = self.get_thumbnail_fetcher(resource_id)
        if fetcher is None:
            return HttpResponseNotFound()

        thumbnail = fetcher.get_thumbnail(True)
        if thumbnail is not None:
            return HttpResponse(thumbnail[0], content_type=thumbnail[1])
        else:
            return HttpResponseNotFound()

    def get_thumbnail_fetcher(self, resource_id):
        factory = SearchThumbnailFetcherFactory()
        fetcher = factory.create_thumbnail_fetcher(resource_id)
        return fetcher
