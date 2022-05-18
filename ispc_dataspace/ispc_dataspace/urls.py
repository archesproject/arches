from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from arches.app.views.plugin import PluginView
from .views.physical_thing_search import PhysicalThingSearchView
from .views.physical_things_in_set import PhysicalThingSetView
from .views.update_resource_list import UpdateResourceListView
from .views.digital_resources_by_object_parts import DigitalResourcesByObjectParts
from .views.auth import SignupView, ConfirmSignupView ##inseriti nuvi
from .views import brochure,projects, heritage_sites, three_d_models, meta_data ##inseriti nuovi

uuid_regex = settings.UUID_REGEX

urlpatterns = [
    url(r'^projects$', projects.ProjectsView.as_view(), name="projects"),
    url(r'^sites$', heritage_sites.HeritageSitesView.as_view(), name="sites"),
    url(r'^3d-models$', three_d_models.ThreeDModelsView.as_view(), name="three_d_models"),
    url(r'^node_values$', meta_data.get_node_values, name="node_values"),
    url(r'^team/', brochure.team, name='team'),
    url(r'^equipment/', brochure.equipment, name='equipment'),
    url(r'^news/', brochure.news, name='news'),
    url(r'^publications/', brochure.publications, name='publications'),
    url(r'^labs/', brochure.labs, name='labs'),
    url(r'^auth/signup$', SignupView.as_view(), name='signup'),
    url(r'^auth/confirm_signup$', ConfirmSignupView.as_view(), name='confirm_signup'),
    url(r"^", include("arches.urls")),
    url(r"^physical-thing-search-results", PhysicalThingSearchView.as_view(), name="physical-thing-search-results"),
    url(r"^physical-things-in-set", PhysicalThingSetView.as_view(), name="physical_things_set"),
    url(
        r"^digital-resources-by-object-parts/(?P<resourceid>%s)$" % uuid_regex,
        DigitalResourcesByObjectParts.as_view(),
        name="digital-resources-by-object-parts",
    ),
    url(r"^updateresourcelist", UpdateResourceListView.as_view(), name="updateresourcelist"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


