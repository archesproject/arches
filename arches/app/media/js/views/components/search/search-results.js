define([
    "jquery",
    "underscore",
    "views/components/search/base-filter",
    "bootstrap",
    "arches",
    "select-woo",
    "knockout",
    "knockout-mapping",
    "models/graph",
    "view-data",
    "templates/views/components/search/search-results.htm",
    "utils/aria",
    "bootstrap-datetimepicker",
], function (
    $,
    _,
    BaseFilter,
    bootstrap,
    arches,
    select2,
    ko,
    koMapping,
    GraphModel,
    viewdata,
    searchResultsTemplate,
    ariaUtils,
) {
    var componentName = "search-results";
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            events: {
                "click .related-resources-graph": "showRelatedResouresGraph",
                "click .navigate-map": "zoomToFeature",
                "mouseover .arches-search-item": "itemMouseover",
                "mouseout .arches-search-item": "itemMouseout",
            },

            initialize: function (options) {
                options.name = 'Search Results';
                BaseFilter.prototype.initialize.call(this, options);
                this.results = ko.observableArray();
                this.showRelationships = ko.observable();
                this.relationshipCandidates = ko.observableArray();
                this.selectedResourceId = ko.observable(null);
                this.language = arches.activeLanguage;
                this.showRelationships.subscribe(function (res) {
                    this.selectedResourceId(res.resourceinstanceid);
                }, this);

                this.searchResults.timestamp.subscribe(function () {
                    this.updateResults();
                }, this);

                this.searchFilterVms[componentName](this);
                this.restoreState();

                this.mapFilter = this.getFilterByType("map-filter-type", false);
                this.mapFilter.subscribe(mapFilter => {
                    if (mapFilter) {
                        this.mapFilter = mapFilter;
                    }
                }, this);
                this.selectedTab.subscribe(function (tab) {
                    if (tab === "map-filter-type") {
                        if (ko.unwrap(this.mapFilter.map)) {
                            this.mapFilter.map().resize();
                        }
                    }
                }, this);

                this.bulkResourceReportCache = ko.observable({});
                this.bulkDisambiguatedResourceInstanceCache = ko.observable({});
                this.shiftFocus = ariaUtils.shiftFocus;
            },

            mouseoverInstance: function () {
                var self = this;
                return function (resourceinstance) {
                    var resourceinstanceid =
                        resourceinstance.resourceinstanceid || "";
                    self.mouseoverInstanceId(resourceinstanceid);
                };
            },

            mouseoverThumbnail: function (_data, event) {
                const largeThumbnail = event.currentTarget.nextElementSibling;
                largeThumbnail.style.display = "block";

                const rect = largeThumbnail.getBoundingClientRect();
                if (rect.bottom > window.innerHeight) {
                    largeThumbnail.style.top =
                        window.innerHeight - rect.height - 60 + "px";
                }
            },

            mouseoutThumbnail: function (_data, event) {
                event.currentTarget.nextElementSibling.style.display = "none";
            },

            showRelatedResources: function () {
                var self = this;
                return function (resourceinstance) {
                    if (resourceinstance === undefined) {
                        resourceinstance =
                            self.relatedResourcesManager.currentResource();
                        if (self.relatedResourcesManager.showGraph() === true) {
                            self.relatedResourcesManager.showGraph(false);
                        }
                    }
                    self.showRelationships(resourceinstance);
                    if (self.selectedTab() !== "related-resources-filter-type") {
                        self.selectedTab("related-resources-filter-type");
                    }
                    self.shiftFocus("#related-resources-filter-type-tabpanel");
                };
            },

            showResourceSummaryReport: function (result) {
                const self = this;
                const resourceId = result._source.resourceinstanceid;

                const reportDataLoaded = ko.observable(false);

                return function () {
                    reportDataLoaded(false);
                    reportDataLoaded.subscribe((loaded) => {
                        if (loaded) {
                            self.details.setupReport(
                                result._source,
                                self.bulkResourceReportCache,
                                self.bulkDisambiguatedResourceInstanceCache,
                            );
                        }
                    });

                    if (
                        !self.bulkDisambiguatedResourceInstanceCache()[
                            resourceId
                        ]
                    ) {
                        const url =
                            arches.urls
                                .api_bulk_disambiguated_resource_instance +
                            `?v=beta&resource_ids=${resourceId}`;

                        self.details.loading(true);

                        $.getJSON(url, (resp) => {
                            const instanceCache =
                                self.bulkDisambiguatedResourceInstanceCache();
                            Object.keys(resp).forEach(function (resourceId) {
                                instanceCache[resourceId] = resp[resourceId];
                            });

                            reportDataLoaded(true);
                            self.shiftFocus(".resource-report");
                            self.bulkDisambiguatedResourceInstanceCache(
                                instanceCache,
                            );
                        });
                    } else {
                        reportDataLoaded(true);
                        self.shiftFocus(".resource-report");
                    }

                    if (self.selectedTab() !== "search-result-details-type") {
                        self.selectedTab("search-result-details-type");
                    }
                };
            },

            updateResults: function () {
                var self = this;
                var data = $('div[name="search-result-data"]').data();

                if (!self.bulkResourceReportCache) {
                    self.bulkResourceReportCache = ko.observable({});
                }

                if (!self.bulkDisambiguatedResourceInstanceCache) {
                    self.bulkDisambiguatedResourceInstanceCache = ko.observable(
                        {},
                    );
                }

                if (!!this.searchResults.results) {
                    this.results.removeAll();
                    this.selectedResourceId(null);

                    var graphIdsToFetch =
                        this.searchResults.results.hits.hits.reduce(function (
                            acc,
                            hit,
                        ) {
                            var graphId = hit["_source"]["graph_id"];

                            if (
                                !ko.unwrap(self.bulkResourceReportCache)[
                                    graphId
                                ]
                            ) {
                                acc.push(graphId);
                            }

                            return acc;
                        }, []);

                    if (graphIdsToFetch.length > 0) {
                        let url =
                            arches.urls.api_bulk_resource_report +
                            `?graph_ids=${graphIdsToFetch}`;

                        $.getJSON(url, function (resp) {
                            var bulkResourceReportCache =
                                self.bulkResourceReportCache();

                            Object.keys(resp).forEach(function (graphId) {
                                var graphData = resp[graphId];

                                if (graphData.graph) {
                                    var graphModel = new GraphModel({
                                        data: graphData.graph,
                                        datatypes: graphData.datatypes,
                                    });
                                    graphData["graphModel"] = graphModel;
                                }

                                bulkResourceReportCache[graphId] = graphData;
                            });

                            self.bulkResourceReportCache(
                                bulkResourceReportCache,
                            );
                        });
                    }

                    var resourceIdsToFetch =
                        this.searchResults.results.hits.hits.reduce(function (
                            acc,
                            hit,
                        ) {
                            var resourceId =
                                hit["_source"]["resourceinstanceid"];

                            if (
                                !ko.unwrap(
                                    self.bulkDisambiguatedResourceInstanceCache,
                                )[resourceId]
                            ) {
                                acc.push(resourceId);
                            }

                            return acc;
                        }, []);

                    this.searchResults.results.hits.hits.forEach(
                        async function (result) {
                            var graphdata = _.find(
                                viewdata.graphs,
                                function (graphdata) {
                                    return (
                                        result._source.graph_id ===
                                        graphdata.graphid
                                    );
                                },
                            );
                            var point = null;
                            if (result._source.points.length > 0) {
                                point = result._source.points[0].point;
                            }

                            const thumbnailUrl = `/thumbnail/${result._source.resourceinstanceid}`;
                            const thumbnailResponse =
                                arches.searchThumbnails == "True"
                                    ? await fetch(thumbnailUrl, {
                                          method: "HEAD",
                                      })
                                    : undefined;
                            const thumbnail =
                                thumbnailResponse && thumbnailResponse.ok
                                    ? thumbnailUrl
                                    : undefined;

                            this.results.push({
                                displayname: result._source.displayname,
                                thumbnail: thumbnail,
                                resourceinstanceid:
                                    result._source.resourceinstanceid,
                                displaydescription:
                                    result._source.displaydescription,
                                alternativelanguage:
                                    result._source.displayname_language !=
                                    arches.activeLanguage,
                                map_popup: result._source.map_popup,
                                provisional_resource:
                                    result._source.provisional_resource,
                                geometries: ko.observableArray(
                                    result._source.geometries,
                                ),
                                iconclass: graphdata ? graphdata.iconclass : "",
                                showrelated: this.showRelatedResources(
                                    result._source.resourceinstanceid,
                                ),
                                showDetails:
                                    this.showResourceSummaryReport(result),
                                mouseoverInstance: this.mouseoverInstance(
                                    result._source.resourceinstanceid,
                                ),
                                mouseoverThumbnail: this.mouseoverThumbnail,
                                mouseoutThumbnail: this.mouseoutThumbnail,
                                relationshipcandidacy:
                                    this.toggleRelationshipCandidacy(
                                        result._source.resourceinstanceid,
                                    ),
                                ontologyclass:
                                    result._source.root_ontology_class,
                                relatable: this.isResourceRelatable(
                                    result._source.graph_id,
                                ),
                                point: point,
                                reportUrl:arches.urls.resource_report+result._source.resourceinstanceid,
                                editUrl:arches.urls.resource_editor+result._source.resourceinstanceid,
                                mapLinkClicked: function () {
                                    self.selectedResourceId(
                                        result._source.resourceinstanceid,
                                    );
                                    if (self.selectedTab() !== "map-filter-type") {
                                        self.selectedTab("map-filter-type");
                                    }
                                    self.mapLinkData({
                                        properties: result._source,
                                    });
                                    self.shiftFocus("canvas.mapboxgl-canvas");
                                },
                                selected: ko.computed(function () {
                                    return (
                                        result._source.resourceinstanceid ===
                                        ko.unwrap(self.selectedResourceId)
                                    );
                                }),
                                isPrincipal: result["is_principal"],
                                canRead: result["can_read"],
                                canEdit: result["can_edit"],
                                // can_delete: result._source.permissions.users_without_delete_perm.indexOf(this.userid) < 0,
                            });
                        },
                        this,
                    );
                }

                return data;
            },

            restoreState: function () {
                this.updateResults();
            },

            viewReport: function (resourceinstance) {
                window.open(
                    arches.urls.resource_report +
                        resourceinstance.resourceinstanceid,
                );
            },

            editResource: function (resourceinstance) {
                window.open(
                    arches.urls.resource_editor +
                        resourceinstance.resourceinstanceid,
                );
            },

            zoomToFeature: function (evt) {
                var data = $(evt.currentTarget).data();
                this.trigger("find_on_map", data.resourceid, data);
            },
        }),
        template: searchResultsTemplate,
    });
});
