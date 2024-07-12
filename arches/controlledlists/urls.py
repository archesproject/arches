from django.urls import path

from arches.controlledlists.views import (
    ListItemView,
    ListView,
    ListsView,
    ListItemImageView,
    ListItemImageMetadataView,
    ListItemValueView,
)

urlpatterns = [
    path("api/controlled_lists/", ListsView.as_view(), name="controlled_lists"),
    path(
        "api/controlled_list/<uuid:list_id>/",
        ListView.as_view(),
        name="controlled_list",
    ),
    path("api/controlled_list/", ListView.as_view(), name="controlled_list_add"),
    path(
        "api/controlled_list_item/<uuid:item_id>/",
        ListItemView.as_view(),
        name="controlled_list_item",
    ),
    path(
        "api/controlled_list_item/",
        ListItemView.as_view(),
        name="controlled_list_item_add",
    ),
    path(
        "api/controlled_list_item_value/<uuid:value_id>/",
        ListItemValueView.as_view(),
        name="controlled_list_item_value",
    ),
    path(
        "api/controlled_list_item_value/",
        ListItemValueView.as_view(),
        name="controlled_list_item_value_add",
    ),
    path(
        "api/controlled_list_item_image/<uuid:image_id>/",
        ListItemImageView.as_view(),
        name="controlled_list_item_image",
    ),
    path(
        "api/controlled_list_item_image/",
        ListItemImageView.as_view(),
        name="controlled_list_item_image_add",
    ),
    path(
        "api/controlled_list_item_image_metadata/<uuid:metadata_id>/",
        ListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata",
    ),
    path(
        "api/controlled_list_item_image_metadata/",
        ListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata_add",
    ),
]
