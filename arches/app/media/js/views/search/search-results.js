define(['jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'arches',
    'select2',
    'knockout',
    'knockout-mapping',
    'view-data',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'],
function($, _, Backbone, bootstrap, arches, select2, ko, koMapping, viewdata) {
    return Backbone.View.extend({

        events: {
            'click .related-resources-graph': 'showRelatedResouresGraph',
            'click .navigate-map': 'zoomToFeature',
            'mouseover .arches-search-item': 'itemMouseover',
            'mouseout .arches-search-item': 'itemMouseout'
        },

        initialize: function(options) {
            var self = this;
            _.extend(this, options);

            this.total = ko.observable();
            this.results = ko.observableArray();
            this.page = ko.observable(1);
            this.paginator = koMapping.fromJS({});
            this.showPaginator = ko.observable(false);
            this.showRelationships = ko.observable();
            this.mouseoverInstanceId = ko.observable();
            this.relationshipCandidates = ko.observableArray();
            this.userRequestedNewPage = ko.observable(false);
            this.mapLinkData = ko.observable(null);
            this.selectedResourceId = ko.observable(null);

            this.showRelationships.subscribe(function(res) {
                self.selectedResourceId(res.resourceinstanceid);
            });
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
                    resourceinstance = self.viewModel.relatedResourcesManager.currentResource();
                    if (self.viewModel.relatedResourcesManager.showGraph() === true) {
                        self.viewModel.relatedResourcesManager.showGraph(false);
                    }
                }
                self.showRelationships(resourceinstance);
                if (self.viewModel.selectedTab() !== self.viewModel.relatedResourcesManager) {
                    self.viewModel.selectedTab(self.viewModel.relatedResourcesManager);
                }
            };
        },

        toggleRelationshipCandidacy: function() {
            var self = this;
            return function(resourceinstanceid){
                var candidate = _.contains(self.relationshipCandidates(), resourceinstanceid);
                if (candidate) {
                    self.relationshipCandidates.remove(resourceinstanceid);
                } else {
                    self.relationshipCandidates.push(resourceinstanceid);
                }
            };
        },

        newPage: function(page){
            if(page){
                this.userRequestedNewPage(true);
                this.page(page);
            }
        },

        isResourceRelatable: function(graphId) {
            var relatable = false;
            if (this.viewModel.graph) {
                relatable = _.contains(this.viewModel.graph.relatable_resource_model_ids, graphId);
            }
            return relatable;
        },

        updateResults: function(response){
            var self = this;
            koMapping.fromJS(response.paginator, this.paginator);
            this.showPaginator(true);
            var data = $('div[name="search-result-data"]').data();

            this.total(response.results.hits.total);
            this.results.removeAll();
            this.userRequestedNewPage(false);
            response.results.aggregations["geo_aggs"] = response.results.aggregations.geo_aggs.inner.buckets[0];
            this.aggregations(
                _.extend(response.results.aggregations, {
                    results: response.results.hits.hits
                })
            );
            this.searchBuffer(response.search_buffer);
            this.selectedResourceId(null);
            this.userIsReviewer = response.reviewer;
            response.results.hits.hits.forEach(function(result){
                var graphdata = _.find(viewdata.graphs, function(graphdata){
                    return result._source.graph_id === graphdata.graphid;
                });
                var point = null;
                if (result._source.points.length > 0) {
                    point = result._source.points[0].point;
                }
                var mapData = result._source.geometries.reduce(function(fc1, fc2) {
                    fc1.geom.features = fc1.geom.features.concat(fc2.geom.features);
                    return fc1;
                }, {
                    "geom": {
                        "type": "FeatureCollection",
                        "features": []
                    }
                });
                this.results.push({
                    displayname: result._source.displayname,
                    resourceinstanceid: result._source.resourceinstanceid,
                    displaydescription: result._source.displaydescription,
                    "map_popup": result._source.map_popup,
                    "provisional_resource": result._source.provisional_resource,
                    geometries: ko.observableArray(result._source.geometries),
                    iconclass: graphdata ? graphdata.iconclass : '',
                    showrelated: this.showRelatedResources(result._source.resourceinstanceid),
                    mouseoverInstance: this.mouseoverInstance(result._source.resourceinstanceid),
                    relationshipcandidacy: this.toggleRelationshipCandidacy(result._source.resourceinstanceid),
                    ontologyclass: result._source.root_ontology_class,
                    relatable: this.isResourceRelatable(result._source.graph_id),
                    point: point,
                    mapLinkClicked: function() {
                        self.selectedResourceId(result._source.resourceinstanceid);
                        if (self.viewModel.selectedTab() !== self.viewModel.mapFilter) {
                            self.viewModel.selectedTab(self.viewModel.mapFilter);
                        }
                        self.mapLinkData(mapData.geom);
                    },
                    selected: ko.computed(function() {
                        return result._source.resourceinstanceid === ko.unwrap(self.selectedResourceId);
                    })
                });
            }, this);

            return data;
        },

        restoreState: function(page){
            if(typeof page !== 'undefined'){
                this.page(ko.utils.unwrapObservable(page));
            }
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

    });
});
