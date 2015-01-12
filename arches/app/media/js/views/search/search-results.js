define(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'knockout',
    'views/related-resources-graph',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, ko, RelatedResourcesGraph, resourceTypes) {

        return Backbone.View.extend({

            events: {
                'click .page-button': 'newPage',
                'click .related-resources-graph': 'showRelatedResouresGraph'
            },

            initialize: function(options) { 
                var self = this;

                this.total = ko.observable();
                this.results = ko.observableArray();
                this.page = ko.observable(1);
                this.paginator = ko.observable();

                ko.applyBindings(this, $('#search-results-list')[0]);
                ko.applyBindings(this, $('#search-results-count')[0]);
                ko.applyBindings(this, $('#paginator')[0]);
            },

            showRelatedResouresGraph: function (e) {
                var resourceId = $(e.target).data('resourceid')
                var searchItem = $(e.target).closest('.arches-search-item');
                var graphPanel = searchItem.find('.arches-related-resource-panel');
                if (!graphPanel.hasClass('view-created')) {
                    new RelatedResourcesGraph({
                        el: graphPanel[0],
                        resourceId: resourceId
                    });
                }
                graphPanel.slideToggle(500);
            },

            newPage: function(evt){
                var data = $(evt.target).data();             
                this.page(data.page);
            },

            updateResults: function(results){
                var self = this;
                this.paginator(results);
                var data = $('div[name="search-result-data"]').data();
                
                this.total(data.results.hits.total);
                self.results.removeAll();
                
                $.each(data.results.hits.hits, function(){
                    self.results.push({
                        primaryname: this._source.primaryname,
                        resourceid: this._source.entityid,
                        entitytypeid: this._source.entitytypeid,
                        descritption: '',
                        geometries: ko.observableArray(this._source.geometries),
                        typeIcon: resourceTypes[this._source.entitytypeid].icon,
                        typeName: resourceTypes[this._source.entitytypeid].name
                    });
                });
            },

            restoreState: function(page){
                if(typeof page !== 'undefined'){
                    this.page(ko.utils.unwrapObservable(page));
                }
            }

        });
    });