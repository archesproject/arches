from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from arches_references.views import (
    ControlledListItemView,
    ControlledListView,
    ControlledListsView,
    ControlledListItemImageView,
    ControlledListItemImageMetadataView,
    ControlledListItemValueView,
)

urlpatterns = [
    path("", include("arches.urls")),
    path(
        "api/controlled_lists/", ControlledListsView.as_view(), name="controlled_lists"
    ),
    path(
        "api/controlled_list/<uuid:list_id>/",
        ControlledListView.as_view(),
        name="controlled_list",
    ),
    path(
        "api/controlled_list/", ControlledListView.as_view(), name="controlled_list_add"
    ),
    path(
        "api/controlled_list_item/<uuid:item_id>/",
        ControlledListItemView.as_view(),
        name="controlled_list_item",
    ),
    path(
        "api/controlled_list_item/",
        ControlledListItemView.as_view(),
        name="controlled_list_item_add",
    ),
    path(
        "api/controlled_list_item_value/<uuid:value_id>/",
        ControlledListItemValueView.as_view(),
        name="controlled_list_item_value",
    ),
    path(
        "api/controlled_list_item_value/",
        ControlledListItemValueView.as_view(),
        name="controlled_list_item_value_add",
    ),
    path(
        "api/controlled_list_item_image/<uuid:image_id>/",
        ControlledListItemImageView.as_view(),
        name="controlled_list_item_image",
    ),
    path(
        "api/controlled_list_item_image/",
        ControlledListItemImageView.as_view(),
        name="controlled_list_item_image_add",
    ),
    path(
        "api/controlled_list_item_image_metadata/<uuid:metadata_id>/",
        ControlledListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata",
    ),
    path(
        "api/controlled_list_item_image_metadata/",
        ControlledListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata_add",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Only handle i18n routing in active project. This will still handle the routes provided by Arches core and Arches applications,
# but handling i18n routes in multiple places causes application errors.
if settings.ROOT_URLCONF == __name__:
    if settings.SHOW_LANGUAGE_SWITCH is True:
        urlpatterns = i18n_patterns(*urlpatterns)

    urlpatterns.append(path("i18n/", include("django.conf.urls.i18n")))
