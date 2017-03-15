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
            },

            mouseoverInstance: function(resourceinstance) {
                var self = this;
                return function(resourceinstance){
                    var resourceinstanceid = resourceinstance.resourceinstanceid || ''
                    self.mouseoverInstanceId(resourceinstanceid);
                }
            },

            newPage: function(page, e){
                if(page){
                    this.page(page);
                }
            },

            showRelatedResources: function(resourceinstanceid) {
                var self = this;
                return function(resourceinstanceid){
                    self.showRelationships(resourceinstanceid)
                }
            },

            toggleRelationshipCandidacy: function(resourceinstanceid) {
                var self = this;
                return function(resourceinstanceid){
                    var candidate = _.contains(self.relationshipCandidates(), resourceinstanceid)
                    if (candidate) {
                        self.relationshipCandidates.remove(resourceinstanceid)
                    } else {
                        self.relationshipCandidates.push(resourceinstanceid)
                    }
                }
            },

            newPage: function(page, e){
                if(page){
                    this.userRequestedNewPage(true);
                    this.page(page);
                }
            },

            updateResults: function(response){
                var self = this;
                koMapping.fromJS(response.paginator, this.paginator);
                this.showPaginator(true);
                var data = $('div[name="search-result-data"]').data();

                this.total(response.results.hits.total);
                this.results.removeAll();
                this.userRequestedNewPage(false);
                this.aggregations(
                    _.extend(response.results.aggregations, {
                        results: response.results.hits.hits
                    })
                );

                response.results.hits.hits.forEach(function(result){
                    var relatable;
                    graphdata = _.find(viewdata.graphs, function(graphdata){
                        return result._source.graph_id === graphdata.graphid;
                    })
                    if (this.viewModel.graph) {
                        relatable = _.contains(this.viewModel.graph.relatable_resource_model_ids, result._source.graph_id);
                    }
                    var point = null;
                    if (result._source.points.length > 0) {
                        point = result._source.points[0]
                    }
                    var mapData = result._source.geometries.reduce(function (fc1, fc2) {
                        fc1.features = fc1.features.concat(fc2.features);
                        return fc1;
                    }, {
                      "type": "FeatureCollection",
                      "features": []
                    });
                    this.results.push({
                        displayname: result._source.displayname,
                        resourceinstanceid: result._source.resourceinstanceid,
                        displaydescription: result._source.displaydescription,
                        map_popup: result._source.map_popup,
                        geometries: ko.observableArray(result._source.geometries),
                        iconclass: graphdata ? graphdata.iconclass : '',
                        showrelated: this.showRelatedResources(result._source.resourceinstanceid),
                        mouseoverInstance: this.mouseoverInstance(result._source.resourceinstanceid),
                        relationshipcandidacy: this.toggleRelationshipCandidacy(result._source.resourceinstanceid),
                        relatable: relatable,
                        point: point,
                        mapLinkClicked: function () {
                            self.mapLinkData(mapData);
                        }
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
