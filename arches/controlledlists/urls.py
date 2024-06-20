from django.urls import path

from arches.controlledlists.views import (
    ControlledListItemView,
    ControlledListView,
    ControlledListsView,
    ControlledListItemImageView,
    ControlledListItemImageMetadataView,
    ControlledListItemValueView,
)

urlpatterns = [
    path(
        "api/controlled_lists/", ControlledListsView.as_view(), name="controlled_lists"
    ),
    path(
        "api/controlled_list/", ControlledListView.as_view(), name="controlled_list_add"
    ),
    path(
        "api/controlled_list/<uuid:id>/",
        ControlledListView.as_view(),
        name="controlled_list",
    ),
    path(
        "api/controlled_list_item/",
        ControlledListItemView.as_view(),
        name="controlled_list_item_add",
    ),
    path(
        "api/controlled_list_item/<uuid:id>/",
        ControlledListItemView.as_view(),
        name="controlled_list_item",
    ),
    path(
        "api/controlled_list_item_value/<uuid:id>/",
        ControlledListItemValueView.as_view(),
        name="controlled_list_item_value",
    ),
    path(
        "api/controlled_list_item_value/",
        ControlledListItemValueView.as_view(),
        name="controlled_list_item_value_add",
    ),
    path(
        "api/controlled_list_item_image/<uuid:id>/",
        ControlledListItemImageView.as_view(),
        name="controlled_list_item_image",
    ),
    path(
        "api/controlled_list_item_image/",
        ControlledListItemImageView.as_view(),
        name="controlled_list_item_image_add",
    ),
    path(
        "api/controlled_list_item_image_metadata/<uuid:id>/",
        ControlledListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata",
    ),
    path(
        "api/controlled_list_item_image_metadata/",
        ControlledListItemImageMetadataView.as_view(),
        name="controlled_list_item_image_metadata_add",
    ),
]
