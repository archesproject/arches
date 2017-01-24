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
                this.showRelationships: ko.observable();
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

            updateResults: function(response){
                var self = this;
                koMapping.fromJS(response.paginator, this.paginator);
                this.showPaginator(true);
                var data = $('div[name="search-result-data"]').data();

                this.total(response.results.hits.total);
                this.results.removeAll();

                response.results.hits.hits.forEach(function(result){
                    var description = "we should probably have a 'Primary Description Function' like we do for primary name";

                    graphdata = _.find(viewdata.graphs, function(graphdata){
                        return result._source.graph_id === graphdata.graphid;
                    })

                    this.results.push({
                        primaryname: result._source.primaryname,
                        resourceinstanceid: result._source.resourceinstanceid,
                        primarydescription: description,
                        geometries: ko.observableArray(result._source.geometries),
                        iconclass: graphdata ? graphdata.iconclass : '',
                        showrelated: this.showRelatedResources(result._source.resourceinstanceid)
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

            itemMouseover: function(evt){
                if(this.currentTarget !== evt.currentTarget){
                    var data = $(evt.currentTarget).data();
                    this.trigger('mouseover', data.resourceid);
                    this.currentTarget = evt.currentTarget;
                }
                return false;
            },

            itemMouseout: function(evt){
                this.trigger('mouseout');
                delete this.currentTarget;
                return false;
            },

            zoomToFeature: function(evt){
                var data = $(evt.currentTarget).data();
                this.trigger('find_on_map', data.resourceid, data);
            }

        });
    });
