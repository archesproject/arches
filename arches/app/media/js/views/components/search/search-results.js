define(['jquery',
    'underscore',
    'views/components/search/base-filter',
    'bootstrap',
    'arches',
    'select2',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'view-data',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'],
function($, _, BaseFilter, bootstrap, arches, select2, ko, koMapping, GraphModel, viewdata) {
    var componentName = 'search-results';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({

            events: {
                'click .related-resources-graph': 'showRelatedResouresGraph',
                'click .navigate-map': 'zoomToFeature',
                'mouseover .arches-search-item': 'itemMouseover',
                'mouseout .arches-search-item': 'itemMouseout'
            },

            initialize: function(options) {
                options.name = 'Search Results';
                this.requiredFilters = ['map-filter'];
                BaseFilter.prototype.initialize.call(this, options);
                this.results = ko.observableArray();
                this.showRelationships = ko.observable();
                this.relationshipCandidates = ko.observableArray();
                this.selectedResourceId = ko.observable(null);

                this.showRelationships.subscribe(function(res) {
                    this.selectedResourceId(res.resourceinstanceid);
                }, this);

                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.updateResults();
                }, this);

                this.filters[componentName](this);
                this.restoreState();
                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(function(){
                        this.mapFilter = this.getFilter('map-filter');
                    }, this);
                } else {
                    this.mapFilter = this.getFilter('map-filter');
                }
                this.selectedTab.subscribe(function(tab){
                    var self = this;
                    if (tab === 'map-filter') {
                        if (ko.unwrap(this.mapFilter.map)) {
                            setTimeout(function() { self.mapFilter.map().resize(); }, 1);
                        }
                    }
                }, this);

                this.bulkResourceReportCache = ko.observable({});
                this.bulkDisambiguatedResourceInstanceCache = ko.observable({});
            },

            mouseoverInstance: function() {
                var self = this;
                return function(resourceinstance){
                    var resourceinstanceid = resourceinstance.resourceinstanceid || '';
                    self.mouseoverInstanceId(resourceinstanceid);
                };
            },

            showRelatedResources: function() {
                var self = this;
                return function(resourceinstance){
                    if (resourceinstance === undefined) {
                        resourceinstance = self.relatedResourcesManager.currentResource();
                        if (self.relatedResourcesManager.showGraph() === true) {
                            self.relatedResourcesManager.showGraph(false);
                        }
                    }
                    self.showRelationships(resourceinstance);
                    if (self.selectedTab() !== 'related-resources-filter') {
                        self.selectedTab('related-resources-filter');
                    }
                };
            },

            showResourceSummaryReport: function(result) {
                const self = this;
                const resourceId = result._source.resourceinstanceid;

                const reportDataLoaded = ko.observable(false);

                return function(){
                    reportDataLoaded(false);

                    if (!self.bulkDisambiguatedResourceInstanceCache()[resourceId]) {
                        const url = arches.urls.api_bulk_disambiguated_resource_instance + `?v=beta&resource_ids=${resourceId}`;
                        
                        self.details.loading(true);

                        $.getJSON(url, (resp) => {
                            const instanceCache = self.bulkDisambiguatedResourceInstanceCache();
                            Object.keys(resp).forEach(function(resourceId) {
                                instanceCache[resourceId] = resp[resourceId];
                            });

                            reportDataLoaded(true);
                            self.bulkDisambiguatedResourceInstanceCache(instanceCache);
                        });
                    }
                    else {
                        reportDataLoaded(true);
                    }
                    
                    reportDataLoaded.subscribe(loaded => {
                        if (loaded) {
                            self.details.setupReport(result._source, self.bulkResourceReportCache, self.bulkDisambiguatedResourceInstanceCache);
                        }
                    });

                    if (self.selectedTab() !== 'search-result-details') {
                        self.selectedTab('search-result-details');
                    }
                };
            },

            updateResults: function(){
                var self = this;
                var data = $('div[name="search-result-data"]').data();

                if (!self.bulkResourceReportCache) {
                    self.bulkResourceReportCache = ko.observable({});
                }

                if (!self.bulkDisambiguatedResourceInstanceCache) {
                    self.bulkDisambiguatedResourceInstanceCache = ko.observable({});
                }
                
                if (!!this.searchResults.results){
                    this.results.removeAll();
                    this.selectedResourceId(null);

                    var graphIdsToFetch = this.searchResults.results.hits.hits.reduce(function(acc, hit) {
                        var graphId = hit['_source']['graph_id'];
                        
                        if (!ko.unwrap(self.bulkResourceReportCache)[graphId]) {
                            acc.push(graphId);
                        }

                        return acc;
                    }, []);

                    if (graphIdsToFetch.length > 0) {
                        let url = arches.urls.api_bulk_resource_report + `?graph_ids=${graphIdsToFetch}`;
    
                        $.getJSON(url, function(resp) {
                            var bulkResourceReportCache = self.bulkResourceReportCache();

                            Object.keys(resp).forEach(function(graphId) {
                                var graphData = resp[graphId];

                                if (graphData.graph) {
                                    var graphModel = new GraphModel({
                                        data: graphData.graph,
                                        datatypes: graphData.datatypes
                                    });
                                    graphData['graphModel'] = graphModel;
                                }

                                bulkResourceReportCache[graphId] = graphData;
                            });

                            self.bulkResourceReportCache(bulkResourceReportCache);
                        });
                    }

                    var resourceIdsToFetch = this.searchResults.results.hits.hits.reduce(function(acc, hit) {
                        var resourceId = hit['_source']['resourceinstanceid'];
                        
                        if (!ko.unwrap(self.bulkDisambiguatedResourceInstanceCache)[resourceId]) {
                            acc.push(resourceId);
                        }

                        return acc;
                    }, []);

                    this.searchResults.results.hits.hits.forEach(function(result){
                        var graphdata = _.find(viewdata.graphs, function(graphdata){
                            return result._source.graph_id === graphdata.graphid;
                        });
                        var point = null;
                        if (result._source.points.length > 0) {
                            point = result._source.points[0].point;
                        }
                        this.results.push({
                            displayname: result._source.displayname,
                            resourceinstanceid: result._source.resourceinstanceid,
                            displaydescription: result._source.displaydescription,
                            "map_popup": result._source.map_popup,
                            "provisional_resource": result._source.provisional_resource,
                            geometries: ko.observableArray(result._source.geometries),
                            iconclass: graphdata ? graphdata.iconclass : '',
                            showrelated: this.showRelatedResources(result._source.resourceinstanceid),
                            showDetails: this.showResourceSummaryReport(result),
                            mouseoverInstance: this.mouseoverInstance(result._source.resourceinstanceid),
                            relationshipcandidacy: this.toggleRelationshipCandidacy(result._source.resourceinstanceid),
                            ontologyclass: result._source.root_ontology_class,
                            relatable: this.isResourceRelatable(result._source.graph_id),
                            point: point,
                            mapLinkClicked: function() {
                                self.selectedResourceId(result._source.resourceinstanceid);
                                if (self.selectedTab() !== 'map-filter') {
                                    self.selectedTab('map-filter');
                                }
                                self.mapLinkData({'properties':result._source});
                            },
                            selected: ko.computed(function() {
                                return result._source.resourceinstanceid === ko.unwrap(self.selectedResourceId);
                            }),
                            canRead: result._source.permissions && result._source.permissions.users_without_read_perm.indexOf(this.userid) < 0 && self.userCanReadResources,
                            canEdit: result._source.permissions && result._source.permissions.users_without_edit_perm.indexOf(this.userid) < 0 && self.userCanEditResources,
                            // can_delete: result._source.permissions.users_without_delete_perm.indexOf(this.userid) < 0,
                        });
                    }, this);
                }

                return data;
            },

            restoreState: function(){
                this.updateResults();
            },

            viewReport: function(resourceinstance){
                window.open(arches.urls.resource_report + resourceinstance.resourceinstanceid);
            },

            editResource: function(resourceinstance){
                window.open(arches.urls.resource_editor + resourceinstance.resourceinstanceid);
            },

            zoomToFeature: function(evt){
                var data = $(evt.currentTarget).data();
                this.trigger('find_on_map', data.resourceid, data);
            }
        }),
        template: { require: 'text!templates/views/components/search/search-results.htm' }
    });
});
