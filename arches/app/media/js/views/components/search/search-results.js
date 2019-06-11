define(['jquery',
    'underscore',
    'views/components/search/base-filter',
    'bootstrap',
    'arches',
    'select2',
    'knockout',
    'knockout-mapping',
    'view-data',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'],
function($, _, BaseFilter, bootstrap, arches, select2, ko, koMapping, viewdata) {
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
                BaseFilter.prototype.initialize.call(this, options);

                this.total = ko.observable();
                this.results = ko.observableArray();
                this.showRelationships = ko.observable();
                this.mouseoverInstanceId = ko.observable();
                this.relationshipCandidates = ko.observableArray();
                this.selectedResourceId = ko.observable(null);
                this.userIsReviewer = ko.observable(false);

                this.showRelationships.subscribe(function(res) {
                    this.selectedResourceId(res.resourceinstanceid);
                }, this);

                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.updateResults();
                }, this);

                this.filters[componentName](this);
                this.restoreState();

                this.mapFilter = this.getFilter('map-filter');
                this.relatedResourcesManager = this.getFilter('related-resources-filter');
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

            updateResults: function(){
                var self = this;
                var data = $('div[name="search-result-data"]').data();

                if (!!this.searchResults.results){
                    this.total(this.searchResults.results.hits.total);
                    this.results.removeAll();
                    this.selectedResourceId(null);
                    this.userIsReviewer(this.searchResults.reviewer);
                    this.searchResults.results.hits.hits.forEach(function(result){
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
                                if (self.selectedTab() !== 'map-filter') {
                                    self.selectedTab('map-filter');
                                }
                                self.mapLinkData(mapData.geom);
                            },
                            selected: ko.computed(function() {
                                return result._source.resourceinstanceid === ko.unwrap(self.selectedResourceId);
                            })
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
