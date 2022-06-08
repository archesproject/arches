from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from arches.app.views import main
from arches.app.views.plugin import PluginView
from afs.views.physical_thing_search import PhysicalThingSearchView
from afs.views.physical_things_in_set import PhysicalThingSetView
from afs.views.update_resource_list import UpdateResourceListView
from afs.views.digital_resources_by_object_parts import DigitalResourcesByObjectParts

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    url(r"^", include("arches.urls")),
    url(r"^errors/404$", main.custom_404, name="construction"),
    url(r"^physical-thing-search-results", PhysicalThingSearchView.as_view(), name="physical-thing-search-results"),
    url(r"^physical-things-in-set", PhysicalThingSetView.as_view(), name="physical_things_set"),
    url(
        r"^digital-resources-by-object-parts/(?P<resourceid>%s)$" % uuid_regex,
        DigitalResourcesByObjectParts.as_view(),
        name="digital-resources-by-object-parts",
    ),
    url(r"^updateresourcelist", UpdateResourceListView.as_view(), name="updateresourcelist"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SHOW_LANGUAGE_SWITCH is True:
    urlpatterns = i18n_patterns(*urlpatterns)
