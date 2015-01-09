require(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'views/resource-search', 
    'views/search/map-filter',
    'views/search/time-filter',
    'views/search/search-results',
    'knockout',
    'plugins/bootstrap-slider/bootstrap-slider.min',
    'views/forms/sections/branch-list',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, ResourceSearch, MapFilter, TimeFilter, SearchResults, ko, Slider, BranchList, resourceTypes) {
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
                    page: this.searchResults.page,
                    q: ko.observableArray(),
                    temporalFilter:  this.timeFilter.query.filter,
                    spatialFilter: this.mapFilter.query.filter,
                    queryString: function(){
                        var params = {
                            page: this.page(),
                            q: ko.toJSON(this.q()),
                            year_min_max: ko.toJSON(this.temporalFilter.year_min_max()),
                            temporalFilter: ko.toJSON(this.temporalFilter.filters()),
                            spatialFilter: ko.toJSON(this.spatialFilter),
                            mapExpanded: self.mapFilter.expanded(),
                            timeExpaned: ''
                        }; 
                        return $.param(params);
                    }, 
                    isEmpty: function(){
                        if (self.mapFilter.query.isEmpty() && 
                            self.searchQuery.q().length === 0 && 
                            self.timeFilter.query.isEmpty()){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.searchQuery.q()) +
                            ko.toJSON(this.searchQuery.temporalFilter.year_min_max()) +
                            ko.toJSON(this.searchQuery.temporalFilter.filters()) +
                            ko.toJSON(this.searchQuery.spatialFilter.geometry.coordinates());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                }

                this.searchQuery.page.subscribe(function(){
                    self.doQuery();
                })

                this.searchQuery.changed.subscribe(function(){
                    self.searchQuery.page(1);
                    self.doQuery();
                });

                this.searchbox = new ResourceSearch({
                    el: $.find('input.resource_search_widget')[0]
                });

                this.searchbox.on('change', function(e, el){
                    if(e.added){
                        self.termFilterViewModel.filters.push(e.added);
                    }
                    if(e.removed){
                        self.termFilterViewModel.filters.remove(e.removed);
                    }
                    self.updateTermFilter();
                });

                this.termFilterViewModel = {
                    filters: ko.observableArray()
                };

                this.getSearchQuery();

            },

            doQuery: function () {
                var self = this;
                var queryString = this.searchQuery.queryString();
                if (this.updateRequest) {
                    this.updateRequest.abort();
                }

                //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
                //window.location = document.location;

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

            toggleFilterSection: function(ele, currentlyExpanded){
                if(!currentlyExpanded){
                    if(this.searchQuery.isEmpty()){
                        this.searchQuery.page(1);
                        this.slideToggle(ele, 'show');
                    }else{
                        
                        this.slideToggle(ele, 'show');
                        this.hideSavedSearches();
                    }
                }else{
                    this.slideToggle(ele, 'hide');               
                }
                return !currentlyExpanded;
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

            updateTermFilter: function(){
                this.searchQuery.q(this.termFilterViewModel.filters());
            },

            getSearchQuery: function(){
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

                if(query.page){
                    query.page = JSON.parse(query.page);
                    this.searchQuery.page(query.page);
                }
                if(query.q){
                    query.q = JSON.parse(query.q);
                    this.searchQuery.q(query.q);
                }
                if(query.temporalFilter){
                    query.temporalFilter = JSON.parse(query.temporalFilter);
                    if(query.temporalFilter.length > 0){
                        this.searchQuery.temporalFilter.filters(query.temporalFilter);
                    }
                }
                if(query.year_min_max){
                    query.year_min_max = JSON.parse(query.year_min_max);
                    if(query.year_min_max.length === 2){
                        this.searchQuery.temporalFilter.year_min_max(query.year_min_max);
                    }
                }
                if(query.spatialFilter){
                    query.spatialFilter = JSON.parse(query.spatialFilter);
                    if(query.spatialFilter.geometry.coordinates.length > 0){
                        this.searchQuery.spatialFilter.geometry.type(ko.utils.unwrapObservable(query.spatialFilter.geometry.type));
                        this.searchQuery.spatialFilter.geometry.coordinates(ko.utils.unwrapObservable(query.spatialFilter.geometry.coordinates));
                        this.searchQuery.spatialFilter.buffer.width(ko.utils.unwrapObservable(query.spatialFilter.buffer.width));
                        this.searchQuery.spatialFilter.buffer.unit(ko.utils.unwrapObservable(query.spatialFilter.buffer.unit));
                    }
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