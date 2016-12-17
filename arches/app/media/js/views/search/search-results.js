define(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'knockout',
    'knockout-mapping',
    'views/related-resources-graph',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, ko, koMapping, RelatedResourcesGraph, resourceTypes) {

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

                //ko.applyBindings(this, $('#search-results-list')[0]);
                //ko.applyBindings(this, $('#search-results-count')[0]);
                //ko.applyBindings(this, $('#paginator')[0]);

            },

            showRelatedResouresGraph: function (e) {
                var resourceId = $(e.target).data('resourceid');
                var primaryName = $(e.target).data('primaryname');
                var typeId = $(e.target).data('entitytypeid');
                var searchItem = $(e.target).closest('.arches-search-item');
                var graphPanel = searchItem.find('.arches-related-resource-panel');
                var nodeInfoPanel = graphPanel.find('.node_info');
                if (!graphPanel.hasClass('view-created')) {
                    new RelatedResourcesGraph({
                        el: graphPanel[0],
                        resourceId: resourceId,
                        resourceName: primaryName,
                        resourceTypeId: typeId
                    });
                }
                nodeInfoPanel.hide();
                $(e.target).closest('li').toggleClass('graph-active');
                graphPanel.slideToggle(500);
            },

            newPage: function(page, e){  
                if(page){
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
                
                response.results.hits.hits.forEach(function(result){
                    var description = "test";//resourceTypes[this._source.entitytypeid].defaultDescription;
                    // var descriptionNode = resourceTypes[this._source.entitytypeid].descriptionNode;
                    // $.each(this._source.child_entities, function(i, entity){
                    //     if (entity.entitytypeid === descriptionNode){
                    //         description = entity.value;
                    //     }
                    // })

                    this.results.push({
                        primaryname: result._source.primaryname,
                        resourceid: result._source.entityid,
                        entitytypeid: result._source.entitytypeid,
                        primarydescription: description,
                        geometries: ko.observableArray(result._source.geometries),
                        // typeIcon: resourceTypes[this._source.entitytypeid].icon,
                        // typeName: resourceTypes[this._source.entitytypeid].name
                    });
                }, this);

                return data;
            },

            restoreState: function(page){
                if(typeof page !== 'undefined'){
                    this.page(ko.utils.unwrapObservable(page));
                }
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