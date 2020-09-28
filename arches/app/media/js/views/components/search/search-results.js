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

            showResourceDetails: function(graphId, result) {
                var self = this;
                return function(){
                    self.details.setupReport(graphId, result._source);
                    if (self.selectedTab() !== 'search-result-details') {
                        self.selectedTab('search-result-details');
                    }
                };
            },

            updateResults: function(){
                var self = this;
                var data = $('div[name="search-result-data"]').data();

                if (!!this.searchResults.results){
                    this.results.removeAll();
                    this.selectedResourceId(null);
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
                            showDetails: this.showResourceDetails(result._source.graph_id, result),
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
                            canRead: result._source.permissions && result._source.permissions.users_without_read_perm.indexOf(this.userid) < 0,
                            canEdit: result._source.permissions && result._source.permissions.users_without_edit_perm.indexOf(this.userid) < 0,
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
