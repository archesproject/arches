"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from arches.app.views.language import LanguageView
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from arches.app.views import concept, main, map, search, graph, api
from arches.app.views.api import auth as api_auth, user as api_user
from arches.app.views.admin import ReIndexResources, ClearUserPermissionCache
from arches.app.views.etl_manager import ETLManagerView
from arches.app.views.file import FileView, TempFileView
from arches.app.views.thumbnail import ThumbnailView
from arches.app.views.graph import (
    GraphDesignerView,
    GraphSettingsView,
    GraphDataView,
    GraphPublicationView,
    GraphManagerView,
    DatatypeTemplateView,
    CardView,
    FunctionManagerView,
    PermissionDataView,
    ModelHistoryView,
    IconDataView,
    NodegroupView,
)
from arches.app.views.resource import (
    ResourceListView,
    ResourceData,
    ResourceCards,
    ResourceReportView,
    RelatedResourcesView,
    ResourceDescriptors,
    ResourceEditLogView,
    ResourceTiles,
    ResourcePermissionDataView,
)
from arches.app.views.resource import (
    ResourceEditorView,
    ResourceActivityStreamPageView,
    ResourceActivityStreamCollectionView,
)
from arches.app.views.plugin import PluginView
from arches.app.views.workflow_history import WorkflowHistoryView
from arches.app.views.concept import RDMView
from arches.app.views.user import UserManagerView
from arches.app.views.tile import TileData
from arches.app.views.transaction import ReverseTransaction
from arches.app.views.notifications import NotificationView
from arches.app.views.map import MapLayerManagerView, TileserverProxyView
from arches.app.views.manifest_manager import ManifestManagerView
from arches.app.views.manifest_manager import IIIFServerProxyView
from arches.app.views.auth import (
    LoginView,
    SignupView,
    ConfirmSignupView,
    ChangePasswordView,
    GetClientIdView,
    UserProfileView,
    ServerSettingView,
    PasswordResetView,
    PasswordResetConfirmView,
    Token,
    TwoFactorAuthenticationLoginView,
    TwoFactorAuthenticationSettingsView,
    TwoFactorAuthenticationResetView,
    ExternalOauth,
)
from arches.app.models.system_settings import settings
from django.urls import path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()
admin.site.login = LoginView.as_view()

uuid_regex = settings.UUID_REGEX


urlpatterns = [
    re_path(r"^$", main.index, name="root"),
    re_path(r"^index.htm", main.index, name="home"),
    re_path(r"^auth/password$", ChangePasswordView.as_view(), name="change_password"),
    re_path(r"^auth/signup$", SignupView.as_view(), name="signup"),
    re_path(
        r"^auth/confirm_signup$", ConfirmSignupView.as_view(), name="confirm_signup"
    ),
    re_path(r"^auth/get_client_id$", GetClientIdView.as_view(), name="get_client_id"),
    re_path(r"^auth/user_profile$", UserProfileView.as_view(), name="user_profile"),
    re_path(
        r"^auth/server_settings$", ServerSettingView.as_view(), name="server_settings"
    ),
    re_path(r"^auth/get_dev_token$", Token.as_view(), name="get_dev_token"),
    re_path(
        r"^auth/eoauth_cb$", ExternalOauth.callback, name="external_oauth_callback"
    ),
    re_path(r"^auth/eoauth_start$", ExternalOauth.start, name="external_oauth_start"),
    re_path(r"^auth/", LoginView.as_view(), name="auth"),
    re_path(r"^rdm/(?P<conceptid>%s|())$" % uuid_regex, RDMView.as_view(), name="rdm"),
    re_path(r"^admin/reindex/resources$", ReIndexResources.as_view(), name="reindex"),
    re_path(
        r"^files/(?P<fileid>%s)$" % uuid_regex, FileView.as_view(), name="file_access"
    ),
    re_path(
        r"^concepts/(?P<conceptid>%s)/manage_parents/$" % uuid_regex,
        concept.manage_parents,
        name="concept_manage_parents",
    ),
    re_path(
        r"^concepts/(?P<conceptid>%s)/confirm_delete/$" % uuid_regex,
        concept.confirm_delete,
        name="confirm_delete",
    ),
    re_path(
        r"^concepts/(?P<conceptid>%s)/make_collection/$" % uuid_regex,
        concept.make_collection,
        name="make_collection",
    ),
    re_path(
        r"^concepts/(?P<conceptid>%s|())$" % uuid_regex, concept.concept, name="concept"
    ),
    re_path(r"^concepts/tree/(?P<mode>.*)", concept.concept_tree, name="concept_tree"),
    re_path(r"^concepts/search$", concept.search, name="concept_search"),
    re_path(
        r"^concepts/(?P<conceptid>%s)/from_sparql_endpoint$" % uuid_regex,
        concept.add_concepts_from_sparql_endpoint,
        name="from_sparql_endpoint",
    ),
    re_path(
        r"^concepts/search_sparql_endpoint$",
        concept.search_sparql_endpoint_for_concepts,
        name="search_sparql_endpoint",
    ),
    re_path(r"^concepts/dropdown", concept.dropdown, name="dropdown"),
    re_path(r"^concepts/paged_dropdown", concept.paged_dropdown, name="paged_dropdown"),
    re_path(
        r"^concepts/export/(?P<conceptid>%s)$" % uuid_regex,
        concept.export,
        name="export_concept",
    ),
    re_path(
        r"^concepts/export/collections",
        concept.export_collections,
        name="export_concept_collections",
    ),
    re_path(
        r"^concepts/collections",
        concept.get_concept_collections,
        name="get_concept_collections",
    ),
    re_path(r"^concepts/get_pref_label", concept.get_pref_label, name="get_pref_label"),
    re_path(r"^conceptvalue/", concept.concept_value, name="concept_value"),
    re_path(r"^search$", search.SearchView.as_view(), name="search_home"),
    re_path(r"^search/terms$", search.search_terms, name="search_terms"),
    re_path(r"^search/resources$", search.search_results, name="search_results"),
    re_path(
        r"^search/time_wheel_config$",
        search.time_wheel_config,
        name="time_wheel_config",
    ),
    re_path(r"^search/export_results$", search.export_results, name="export_results"),
    re_path(
        r"^search/get_export_file$", search.get_export_file, name="get_export_file"
    ),
    re_path(r"^search/get_dsl$", search.get_dsl_from_search_string, name="get_dsl"),
    re_path(r"^buffer/$", search.buffer, name="buffer"),
    re_path(
        r"^settings/",
        ResourceEditorView.as_view(),
        {
            "resourceid": settings.RESOURCE_INSTANCE_ID,
            "view_template": "views/resource/editor.htm",
            "main_script": "views/resource/editor",
            "nav_menu": False,
        },
        name="config",
    ),
    re_path(
        r"^graph/new$", GraphDataView.as_view(action="new_graph"), name="new_graph"
    ),
    re_path(
        r"^graph/import/",
        GraphDataView.as_view(action="import_graph"),
        name="import_graph",
    ),
    re_path(
        r"^graph/reorder_nodes$",
        GraphDataView.as_view(action="reorder_nodes"),
        name="reorder_nodes",
    ),
    re_path(
        r"^graph/permissions$", PermissionDataView.as_view(), name="permission_data"
    ),
    re_path(
        r"^resource/permissions$",
        ResourcePermissionDataView.as_view(),
        name="resource_permission_data",
    ),
    re_path(
        r"^graph/permissions/permission_manager_data$",
        PermissionDataView.as_view(action="get_permission_manager_data"),
        name="permission_manager_data",
    ),
    re_path(
        r"^graph/(?P<graphid>%s|())$" % uuid_regex,
        GraphManagerView.as_view(),
        name="graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/nodes$" % uuid_regex,
        GraphDataView.as_view(action="get_nodes"),
        name="graph_nodes",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/append_branch$" % uuid_regex,
        GraphDataView.as_view(action="append_branch"),
        name="append_branch",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/append_node$" % uuid_regex,
        GraphDataView.as_view(action="append_node"),
        name="append_node",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/move_node$" % uuid_regex,
        GraphDataView.as_view(action="move_node"),
        name="move_node",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/update_node$" % uuid_regex,
        GraphDataView.as_view(action="update_node"),
        name="update_node",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/delete_node$" % uuid_regex,
        GraphDataView.as_view(action="delete_node"),
        name="delete_node",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/delete_instances$" % uuid_regex,
        GraphDataView.as_view(action="delete_instances"),
        name="delete_instances",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/clone$" % uuid_regex,
        GraphDataView.as_view(action="clone_graph"),
        name="clone_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/export$" % uuid_regex,
        GraphDataView.as_view(action="export_graph"),
        name="export_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/delete$" % uuid_regex,
        GraphDataView.as_view(action="delete_graph"),
        name="delete_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/export_branch$" % uuid_regex,
        GraphDataView.as_view(action="export_branch"),
        name="export_branch",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/export_mapping_file$" % uuid_regex,
        GraphDataView.as_view(action="export_mapping_file"),
        name="export_mapping_file",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/get_related_nodes/(?P<nodeid>%s)$"
        % (uuid_regex, uuid_regex),
        GraphDataView.as_view(action="get_related_nodes"),
        name="get_related_nodes",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/get_valid_domain_nodes/(?P<nodeid>%s|())$"
        % (uuid_regex, uuid_regex),
        GraphDataView.as_view(action="get_valid_domain_nodes"),
        name="get_valid_domain_nodes",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/get_domain_connections$" % uuid_regex,
        GraphDataView.as_view(action="get_domain_connections"),
        name="get_domain_connections",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/publish$" % uuid_regex,
        GraphPublicationView.as_view(action="publish"),
        name="publish_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/revert$" % uuid_regex,
        GraphPublicationView.as_view(action="revert"),
        name="revert_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/restore_state_from_serialized_graph$" % uuid_regex,
        GraphPublicationView.as_view(action="restore_state_from_serialized_graph"),
        name="restore_state_from_serialized_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/update_published_graphs$" % uuid_regex,
        GraphPublicationView.as_view(action="update_published_graphs"),
        name="update_published_graphs",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/model_history$" % uuid_regex,
        ModelHistoryView.as_view(),
        name="model_history",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/update_published_graph$" % uuid_regex,
        ModelHistoryView.as_view(),
        name="update_published_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/delete_published_graph$" % uuid_regex,
        ModelHistoryView.as_view(),
        name="delete_published_graph",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/function_manager$" % uuid_regex,
        FunctionManagerView.as_view(),
        name="function_manager",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/apply_functions$" % uuid_regex,
        FunctionManagerView.as_view(),
        name="apply_functions",
    ),
    re_path(
        r"^graph/(?P<graphid>%s)/remove_functions$" % uuid_regex,
        FunctionManagerView.as_view(),
        name="remove_functions",
    ),
    re_path(
        r"^graph_designer/(?P<graphid>%s)$" % uuid_regex,
        GraphDesignerView.as_view(),
        name="graph_designer",
    ),
    re_path(
        r"^graph_settings/(?P<graphid>%s)$" % uuid_regex,
        GraphSettingsView.as_view(),
        name="graph_settings",
    ),
    re_path(
        r"^components/datatypes/(?P<template>[a-zA-Z_-]*)",
        DatatypeTemplateView.as_view(),
        name="datatype_template",
    ),
    re_path(r"^resource$", ResourceListView.as_view(), name="resource"),
    re_path(
        r"^resource/(?P<resourceid>%s)$" % uuid_regex,
        ResourceEditorView.as_view(),
        name="resource_editor",
    ),
    re_path(
        r"^add-resource/(?P<graphid>%s)$" % uuid_regex,
        ResourceEditorView.as_view(),
        name="add_resource",
    ),
    re_path(
        r"^resource/(?P<resourceid>%s)/copy$" % uuid_regex,
        ResourceEditorView.as_view(action="copy"),
        name="resource_copy",
    ),
    re_path(
        r"^resource/(?P<resourceid>%s)/history$" % uuid_regex,
        ResourceEditLogView.as_view(),
        name="resource_edit_log",
    ),
    re_path(
        r"^resource/(?P<resourceid>%s)/data/(?P<formid>%s)$" % (uuid_regex, uuid_regex),
        ResourceData.as_view(),
        name="resource_data",
    ),
    re_path(
        r"^resource/(?P<resourceid>%s)/cards$" % uuid_regex,
        ResourceCards.as_view(),
        name="resource_cards",
    ),
    re_path(r"^resource/history$", ResourceEditLogView.as_view(), name="edit_history"),
    re_path(
        r"^resource/related/(?P<resourceid>%s|())$" % uuid_regex,
        RelatedResourcesView.as_view(),
        name="related_resources",
    ),
    re_path(
        r"^resource/related/candidates",
        RelatedResourcesView.as_view(action="get_candidates"),
        name="related_resource_candidates",
    ),
    re_path(
        r"^resource/related/relatable",
        RelatedResourcesView.as_view(action="get_relatable_resources"),
        name="relatable_resources",
    ),
    re_path(
        r"^resource/descriptors/(?P<resourceid>%s|())$" % uuid_regex,
        ResourceDescriptors.as_view(),
        name="resource_descriptors",
    ),
    re_path(
        r"^resource/(?P<resourceid>%s)/tiles$" % uuid_regex,
        ResourceTiles.as_view(),
        name="resource_tiles",
    ),
    re_path(
        r"^report/(?P<resourceid>%s)$" % uuid_regex,
        ResourceReportView.as_view(),
        name="resource_report",
    ),
    re_path(
        r"^transaction/(?P<transactionid>%s)/reverse$" % uuid_regex,
        ReverseTransaction.as_view(),
        name="transaction_reverse",
    ),
    re_path(
        r"^card/(?P<cardid>%s|())$" % uuid_regex,
        CardView.as_view(action="update_card"),
        name="card",
    ),
    re_path(
        r"^reorder_cards/",
        CardView.as_view(action="reorder_cards"),
        name="reorder_cards",
    ),
    re_path(
        r"^node/(?P<graphid>%s)$" % uuid_regex,
        GraphDataView.as_view(action="update_node"),
        name="node",
    ),
    re_path(
        r"^nodegroup/", NodegroupView.as_view(action="exportable"), name="nodegroup"
    ),
    re_path(r"^language/", LanguageView.as_view(), name="language"),
    re_path(
        r"^node_layer/(?P<graphid>%s)$" % uuid_regex,
        GraphDataView.as_view(action="update_node_layer"),
        name="node_layer",
    ),
    re_path(r"^widgets/(?P<template>[a-zA-Z_-]*)", main.widget, name="widgets"),
    re_path(
        r"^report-templates/(?P<template>[a-zA-Z_-]*)",
        main.report_templates,
        name="report-templates",
    ),
    re_path(
        r"^function-templates/(?P<template>[a-zA-Z_-]*)",
        main.function_templates,
        name="function-templates",
    ),
    re_path(r"^help-templates$", main.help_templates, name="help_templates"),
    re_path(
        r"^temp_file/(?P<file_id>[^\/]+)", TempFileView.as_view(), name="temp_file"
    ),
    re_path(r"^temp_file$", TempFileView.as_view(), name="temp_file"),
    re_path(r"^tile$", TileData.as_view(action="update_tile"), name="tile"),
    re_path(
        r"^tiles/reorder_tiles$",
        TileData.as_view(action="reorder_tiles"),
        name="reorder_tiles",
    ),
    re_path(
        r"^tiles/tile_history$",
        TileData.as_view(action="tile_history"),
        name="tile_history",
    ),
    re_path(
        r"^tiles/delete_provisional_tile$",
        TileData.as_view(action="delete_provisional_tile"),
        name="delete_provisional_tile",
    ),
    re_path(
        r"^tiles/download_files$",
        TileData.as_view(action="download_files"),
        name="download_files",
    ),
    re_path(
        r"^templates/(?P<template>[a-zA-Z_\-./]*)", main.templates, name="templates"
    ),
    re_path(
        r"^map_layer_manager/(?P<maplayerid>%s)$" % uuid_regex,
        MapLayerManagerView.as_view(),
        name="map_layer_update",
    ),
    re_path(
        r"^map_layer_manager/*", MapLayerManagerView.as_view(), name="map_layer_manager"
    ),
    re_path(
        r"^feature_popup_content$",
        main.feature_popup_content,
        name="feature_popup_content",
    ),
    re_path(r"^user$", UserManagerView.as_view(), name="user_profile_manager"),
    re_path(
        r"^user/get_user_names$",
        UserManagerView.as_view(action="get_user_names"),
        name="get_user_names",
    ),
    re_path(r"^notifications$", NotificationView.as_view(), name="get_notifications"),
    re_path(
        r"^notifications/dismiss$",
        NotificationView.as_view(action="dismiss"),
        name="dismiss_notifications",
    ),
    re_path(
        r"^notifications/get_types$",
        NotificationView.as_view(action="get_types"),
        name="get_notification_types",
    ),
    re_path(
        r"^notifications/update_types$",
        NotificationView.as_view(action="update_types"),
        name="update_notification_types",
    ),
    re_path(
        r"^%s/(?P<path>.*)$" % settings.KIBANA_CONFIG_BASEPATH,
        api.KibanaProxy.as_view(),
    ),
    re_path(
        r"^graphs/(?P<graph_id>%s)$" % (uuid_regex),
        api.Graphs.as_view(),
        name="graphs_api",
    ),
    re_path(
        r"^graphs",
        api.Graphs.as_view(action="get_graph_models"),
        name="get_graph_models_api",
    ),
    re_path(
        r"^graph_is_active/(?P<graph_id>%s)$" % (uuid_regex),
        api.GraphIsActive.as_view(),
        name="graph_is_active_api",
    ),
    re_path(
        r"^resources/(?P<graphid>%s)/(?P<resourceid>%s|())$" % (uuid_regex, uuid_regex),
        api.Resources.as_view(),
        name="resources_graphid",
    ),
    re_path(
        r"^resources/(?P<slug>[-\w]+)/(?P<resourceid>%s|())$" % uuid_regex,
        api.Resources.as_view(),
        name="resources_slug",
    ),
    re_path(
        r"^resources/(?P<resourceid>%s|())$" % uuid_regex,
        api.Resources.as_view(),
        name="resources",
    ),
    path("api/login", api_auth.Login.as_view(), name="api_login"),
    path("api/logout", api_auth.Logout.as_view(), name="api_logout"),
    path("api/user", api_user.UserView.as_view(), name="api_user"),
    re_path(
        r"^api/tiles/(?P<tileid>%s|())$" % (uuid_regex),
        api.Tile.as_view(),
        name="api_tiles",
    ),
    re_path(
        r"^api/nodes/(?P<nodeid>%s|())$" % (uuid_regex),
        api.Node.as_view(),
        name="api_nodes",
    ),
    re_path(
        r"^api/nodegroup/(?P<nodegroupid>%s|())$" % (uuid_regex),
        api.NodeGroup.as_view(),
        name="api_nodegroup",
    ),
    re_path(
        r"^api/instance_permissions/$",
        api.InstancePermission.as_view(),
        name="api_instance_permissions",
    ),
    re_path(r"^api/node_value/$", api.NodeValue.as_view(), name="api_node_value"),
    re_path(
        r"^api/resource_instance_lifecycle/$",
        api.ResourceInstanceLifecycleStates.as_view(),
        name="api_resource_instance_lifecycle_states",
    ),
    re_path(
        r"^api/resource_instance_lifecycle_state/(?P<resourceid>%s|())$" % (uuid_regex),
        api.ResourceInstanceLifecycleState.as_view(),
        name="api_resource_instance_lifecycle_state",
    ),
    re_path(
        r"^api/resource_report/(?P<resourceid>%s|())$" % (uuid_regex),
        api.ResourceReport.as_view(),
        name="api_resource_report",
    ),
    re_path(
        r"^api/bulk_resource_report$",
        api.BulkResourceReport.as_view(),
        name="api_bulk_resource_report",
    ),
    re_path(
        r"^api/bulk_disambiguated_resource_instance$",
        api.BulkDisambiguatedResourceInstance.as_view(),
        name="api_bulk_disambiguated_resource_instance",
    ),
    re_path(
        r"^api/get_frontend_i18n_data$",
        api.GetFrontendI18NData.as_view(),
        name="get_frontend_i18n_data",
    ),
    re_path(
        r"^api/search/export_results$",
        api.SearchExport.as_view(),
        name="api_export_results",
    ),
    re_path(
        r"^api/user_incomplete_workflows$",
        api.UserIncompleteWorkflows.as_view(),
        name="api_user_incomplete_workflows",
    ),
    re_path(
        r"^api/plugins/(?P<pluginid>%s)?$" % uuid_regex,
        api.Plugins.as_view(),
        name="api_plugins",
    ),
    re_path(
        r"^api/get_nodegroup_tree$",
        api.GetNodegroupTree.as_view(),
        name="api_get_nodegroup_tree",
    ),
    re_path(
        r"^rdm/concepts/(?P<conceptid>%s|())$" % uuid_regex,
        api.Concepts.as_view(),
        name="concepts",
    ),
    path("plugins/<uuid:pluginid>", PluginView.as_view(), name="plugins"),
    path("plugins/<uuid:pluginid>/<path:path>", PluginView.as_view(), name="plugins"),
    path("plugins/<slug:slug>", PluginView.as_view(), name="plugins"),
    path("plugins/<slug:slug>/<path:path>", PluginView.as_view(), name="plugins"),
    re_path(
        r"^workflow_history/(?P<workflowid>%s|())$" % uuid_regex,
        WorkflowHistoryView.as_view(),
        name="workflow_history",
    ),
    re_path(
        r"^cards/(?P<resourceid>%s|())$" % uuid_regex,
        api.Card.as_view(),
        name="api_card",
    ),
    re_path(
        r"^search_component_data/(?P<componentname>[-\w]+)$",
        api.SearchComponentData.as_view(),
        name="api_search_component_data",
    ),
    re_path(r"^geojson$", api.GeoJSON.as_view(), name="geojson"),
    re_path(
        r"^mvt/(?P<nodeid>%s)/(?P<zoom>[0-9]+|\{z\})/(?P<x>[0-9]+|\{x\})/(?P<y>[0-9]+|\{y\}).pbf$"
        % uuid_regex,
        api.MVT.as_view(),
        name="mvt",
    ),
    re_path(r"^images$", api.Images.as_view(), name="images"),
    re_path(
        r"^ontology_properties$",
        api.OntologyProperty.as_view(),
        name="ontology_properties",
    ),
    re_path(
        r"^validate/(?P<itemtype>[-\w]+)/(?P<itemid>[-\w]+)",
        api.Validator.as_view(),
        name="validate",
    ),
    re_path(
        r"^validate/(?P<itemtype>[-\w]+)", api.Validator.as_view(), name="validatejson"
    ),
    re_path(r"^tileserver/(?P<path>.*)$", TileserverProxyView.as_view()),
    re_path(
        r"^history/$",
        ResourceActivityStreamCollectionView.as_view(),
        name="as_stream_collection",
    ),
    re_path(
        r"^history/(?P<page>[0-9]+)$",
        ResourceActivityStreamPageView.as_view(),
        name="as_stream_page",
    ),
    re_path(r"^icons$", IconDataView.as_view(), name="icons"),
    re_path(
        r"^thumbnail/(?P<resource_id>%s)$" % uuid_regex,
        ThumbnailView.as_view(),
        name="thumbnail",
    ),
    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    re_path(r"^admin/", admin.site.urls),
    re_path(
        r"^password_reset/$",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    re_path(
        r"^password_reset/done/$",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        r"^reset/done/$",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    re_path(r"^o/", include("oauth2_provider.urls", namespace="oauth2")),
    re_path(r"^iiifmanifest$", api.IIIFManifest.as_view(), name="iiifmanifest"),
    re_path(r"^iiifserver/(?P<path>.*)$", IIIFServerProxyView.as_view()),
    re_path(
        r"^iiifannotations$", api.IIIFAnnotations.as_view(), name="iiifannotations"
    ),
    re_path(
        r"^iiifannotationnodes$",
        api.IIIFAnnotationNodes.as_view(),
        name="iiifannotationnodes",
    ),
    re_path(r"^manifest/(?P<id>[0-9]+)$", api.Manifest.as_view(), name="manifest"),
    re_path(
        r"^manifest/(?P<id>%s)$" % uuid_regex, api.Manifest.as_view(), name="manifest"
    ),
    re_path(
        r"^image-service-manager",
        ManifestManagerView.as_view(),
        name="manifest_manager",
    ),
    re_path(
        r"^two-factor-authentication-settings",
        TwoFactorAuthenticationSettingsView.as_view(),
        name="two-factor-authentication-settings",
    ),
    re_path(
        r"^two-factor-authentication-login",
        TwoFactorAuthenticationLoginView.as_view(),
        name="two-factor-authentication-login",
    ),
    re_path(
        r"^two-factor-authentication-reset",
        TwoFactorAuthenticationResetView.as_view(),
        name="two-factor-authentication-reset",
    ),
    re_path(r"^etl-manager$", ETLManagerView.as_view(), name="etl_manager"),
    re_path(
        r"^clear-user-permission-cache",
        ClearUserPermissionCache.as_view(),
        name="clear_user_permission_cache",
    ),
    re_path(
        r"^transform-edtf-for-tile",
        api.TransformEdtfForTile.as_view(),
        name="transform_edtf_for_tile",
    ),
    re_path(
        r"^api/spatialview/(?P<identifier>%s|())/?$" % uuid_regex,
        api.SpatialView.as_view(),
        name="spatialview_api",
    ),
]

handler400 = "arches.app.views.main.custom_400"
handler403 = "arches.app.views.main.custom_403"
handler404 = "arches.app.views.main.custom_404"
handler500 = "arches.app.views.main.custom_500"

# This must be included in core to keep webpack happy, but cannot be appended when running a project.
# See https://github.com/archesproject/arches/pull/10754
if settings.ROOT_URLCONF == __name__:
    if settings.SHOW_LANGUAGE_SWITCH is True:
        urlpatterns = i18n_patterns(*urlpatterns)

    urlpatterns.append(path("i18n/", include("django.conf.urls.i18n")))


if settings.DEBUG:
    try:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
    except:
        pass
