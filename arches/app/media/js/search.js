require(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'views/search/term-filter', 
    'views/search/map-filter',
    'views/search/time-filter',
    'views/search/search-results',
    'knockout',
    'plugins/bootstrap-slider/bootstrap-slider.min',
    'views/forms/sections/branch-list',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, TermFilter, MapFilter, TimeFilter, SearchResults, ko, Slider, BranchList, resourceTypes) {
    $(document).ready(function() {

        var SearchView = Backbone.View.extend({
            el: $('body'),
            updateRequest: '',

            events: {
                'click #view-saved-searches': 'showSavedSearches',
                'click #map-filter-button': 'toggleMapFilter',
                'click #time-filter-button': 'toggleTimeFilter'
            },

            initialize: function(options) { 
                var self = this;
                var initialcount = $('#search-results-count').data().count;

                this.termFilter = new TermFilter({
                    el: $.find('input.resource_search_widget')[0]
                });

                this.mapFilter = new MapFilter({
                    el: $('#map-filter-container')[0]
                });

                this.timeFilter = new TimeFilter({
                    el: $('#time-filter-container')[0]
                });

                this.searchResults = new SearchResults({
                    el: $('#search-results-container')[0]
                });

                this.searchQuery = {
                    queryString: function(){
                        var params = {
                            page: self.searchResults.page(),
                            termFilter: ko.toJSON(self.termFilter.query.filter.terms()),
                            year_min_max: ko.toJSON(self.timeFilter.query.filter.year_min_max()),
                            temporalFilter: ko.toJSON(self.timeFilter.query.filter.filters()),
                            spatialFilter: ko.toJSON(self.mapFilter.query.filter),
                            mapExpanded: self.mapFilter.expanded(),
                            timeExpaned: self.timeFilter.expanded()
                        }; 
                        return $.param(params);
                    }, 
                    isEmpty: function(){
                        if (self.mapFilter.query.isEmpty() && 
                            self.termFilter.query.isEmpty() && 
                            self.timeFilter.query.isEmpty()){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.termFilter.query.changed()) +
                            ko.toJSON(this.timeFilter.query.changed()) +
                            ko.toJSON(this.mapFilter.query.changed());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                }

                this.getSearchQuery();

                this.searchResults.page.subscribe(function(){
                    self.doQuery();
                })

                this.searchQuery.changed.subscribe(function(){
                    self.searchResults.page(1);
                    self.doQuery();
                });
            },

            doQuery: function () {
                var self = this;
                var queryString = this.searchQuery.queryString();
                if (this.updateRequest) {
                    this.updateRequest.abort();
                }

                window.history.pushState({}, '', '?'+queryString);

                this.updateRequest = $.ajax({
                    type: "GET",
                    url: arches.urls.search_results,
                    data: queryString,
                    success: function(results){
                        self.searchResults.updateResults(results);
                        self.toggleSearchResults('show');
                        self.toggleSavedSearches('hide');
                        self.mapFilter.applyBuffer();
                    },
                    error: function(){}
                });
            },

            showSavedSearches: function(){
                this.toggleSavedSearches('show');
                this.toggleSearchResults('hide');
            },

            hideSavedSearches: function(){
                this.toggleSavedSearches('hide');
                this.toggleSearchResults('show');
            },

            toggleSavedSearches: function(showOrHide){
                var ele = $('#saved-searches');
                this.slideToggle(ele, showOrHide);
            },

            toggleSearchResults: function(showOrHide){
                var ele = $('#search-results');
                this.slideToggle(ele, showOrHide);
            },

            toggleMapFilter: function(){
                if($('#saved-searches').is(":visible")){
                    this.doQuery();
                }
                this.mapFilter.expanded(!this.mapFilter.expanded());
            },

            toggleTimeFilter: function(showOrHide){
                if($('#saved-searches').is(":visible")){
                    this.doQuery();
                }
                this.timeFilter.expanded(!this.timeFilter.expanded());
            },

            slideToggle: function(ele, showOrHide){
                var self = this;
                if ($(ele).is(":visible") && showOrHide === 'hide'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!($(ele).is(":visible")) && showOrHide === 'show'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!showOrHide){
                    ele.slideToggle('slow');                    
                }
            },

            getSearchQuery: function(){
                var doQuery = false;
                var query = _.chain(decodeURIComponent(location.search).slice(1).split('&') )
                    // Split each array item into [key, value]
                    // ignore empty string if search is empty
                    .map(function(item) { if (item) return item.split('='); })
                    // Remove undefined in the case the search is empty
                    .compact()
                    // Turn [key, value] arrays into object parameters
                    .object()
                    // Return the value of the chain operation
                    .value();

                if('page' in query){
                    this.searchResults.page(JSON.parse(query.page));
                    doQuery = true;
                }
                if('termFilter' in query){
                    this.termFilter.query.filter.terms(JSON.parse(query.termFilter));
                    doQuery = true;
                }
                if('temporalFilter' in query){
                    query.temporalFilter = JSON.parse(query.temporalFilter);
                    if(query.temporalFilter.length > 0){
                        this.timeFilter.query.filter.filters(query.temporalFilter);
                        doQuery = true;
                    }
                }
                if('year_min_max' in query){
                    query.year_min_max = JSON.parse(query.year_min_max);
                    if(query.year_min_max.length === 2){
                        this.timeFilter.query.filter.year_min_max(query.year_min_max);
                        doQuery = true;
                    }
                }
                if('spatialFilter' in query){
                    query.spatialFilter = JSON.parse(query.spatialFilter);
                    if(query.spatialFilter.geometry.coordinates.length > 0){
                        this.mapFilter.query.filter.geometry.type(ko.utils.unwrapObservable(query.spatialFilter.geometry.type));
                        this.mapFilter.query.filter.geometry.coordinates(ko.utils.unwrapObservable(query.spatialFilter.geometry.coordinates));
                        this.mapFilter.query.filter.buffer.width(ko.utils.unwrapObservable(query.spatialFilter.buffer.width));
                        this.mapFilter.query.filter.buffer.unit(ko.utils.unwrapObservable(query.spatialFilter.buffer.unit));
                        doQuery = true;

                        var coordinates = this.mapFilter.query.filter.geometry.coordinates();
                        var type = this.mapFilter.query.filter.geometry.type();
                        if(type === 'bbox'){
                            this.mapFilter.zoomToExtent(coordinates);
                        }else{
                            this.mapFilter.zoomToExtent(new ol.geom[type](coordinates).getExtent());
                        }
                    }
                }
                if('mapExpanded' in query){
                    this.mapFilter.expanded(JSON.parse(query.mapExpanded))
                }
                if('timeExpanded' in query){
                    this.timeFilter.expanded(JSON.parse(query.timeExpanded))
                }

                if(doQuery){
                    this.doQuery();
                }
                

                window.onpopstate = function(event) {
                  //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
                    //window.location = document.location;
                };
            }

        });
        new SearchView();
    });
});