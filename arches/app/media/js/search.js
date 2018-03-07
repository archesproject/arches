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
    'openlayers',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, TermFilter, MapFilter, TimeFilter, SearchResults, ko, Slider, BranchList, resourceTypes, ol) {
    $(document).ready(function() {
        var wkt = new ol.format.WKT();

        var SearchView = Backbone.View.extend({
            el: $('body'),
            updateRequest: '',

            events: {
                'click #view-saved-searches': 'showSavedSearches',
                'click #clear-search': 'clear',
                'click #map-filter-button': 'clickMapFilter',
                'click #map-filter-button .close-btn': 'closeMapFilter',
                'click .time-filter-button': 'toggleTimeFilter',
                'click a.dataexport': 'exportSearch',
                'click a.search-and-or': 'onChangeAndOr',
                'click .toggle-related-resources': 'onClickRelatedResources',
                'click a.search-term-and-or': 'onChangeTermAndOr',
                'click .toggle-combine-prev': 'onChangeCombineWithPrev',
                'click a.search-grouped': 'onChangeGroup',
                'click .add-search-box': 'onAddSearchBox',
                'click .remove-search-box': 'onRemoveSearchBox',
                'click .advanced-search': 'onToggleAdvancedSearch',
            },

            initialize: function(options) {
                var self = this;
                var query = this.getQueryFromUrl();
                if('termFilter' in query){
                    query.termFilter = JSON.parse(query.termFilter);
                    query.termFilter = _.filter(query.termFilter , function(filter){ return filter.length > 0 });
                    this.searchBoxes = query.termFilter.length;
                    if (this.searchBoxes < 1) {
                        this.searchBoxes = 1;
                    }
                } else {
                    this.searchBoxes = 1;
                }
                // searchboxes for advanced search should be at least one, even for a new search
                this.initializeSearchBoxes();

                this.mapFilter = new MapFilter({
                    el: $('#map-filter-container')[0]
                });
                this.mapFilter.on('enabled', function(enabled, inverted){
                    if(enabled){
                        // this.termFilter[0].addTag(this.mapFilterText, inverted);
                        $("#map-filter-button").addClass("enabled");
                    }else{
                        // this.termFilter[0].removeTag(this.mapFilterText);
                        $("#map-filter-button").removeClass("enabled");
                        // this.mapFilter.clear();
                    }
                    this.mapFilter.inverted = inverted;
                    if(inverted){
                        $("#map-filter-button").addClass("inverted");
                    }else{
                        $("#map-filter-button").removeClass("inverted");
                    }
                }, this);

                this.booleanSearch = "and";
                this.searchRelatedResources = false;
                this.advancedSearch = false;

                this.searchResults = new SearchResults({
                    el: $('#search-results-container')[0]
                });
                this.searchResults.on('mouseover', function(resourceid){
                    this.mapFilter.selectFeatureById(resourceid);
                }, this);
                this.searchResults.on('mouseout', function(){
                    this.mapFilter.unselectAllFeatures();
                }, this);
                this.searchResults.on('find_on_map', function(resourceid, data){
                    var extent,
                        expand = !this.mapFilter.expanded();
                    if (expand) {
                        this.mapFilter.expanded(true);
                    }
                    
                    _.each(data.geometries, function (geometryData) {
                        var geomExtent = wkt.readGeometry(geometryData.label).getExtent();
                        geomExtent = ol.extent.applyTransform(geomExtent, ol.proj.getTransform('EPSG:4326', 'EPSG:3857'));
                        extent = extent ? ol.extent.extend(extent, geomExtent) : geomExtent;
                    });
                    if (extent) {
                        _.delay(function() {
                            self.mapFilter.zoomToExtent(extent);
                        }, expand ? 700 : 0);
                    }
                }, this);


                this.mapFilterText = this.mapFilter.$el.data().filtertext;
                this.timeFilterText = $('#time-filter-container-template').data().filtertext;
                self.isNewQuery = true;
                this.searchQuery = {
                    queryString: function(){
                        if (self.advancedSearch) {
                            var termFilters = [];
                            var timeFilters = [];
                            var termFiltersLen = 0;
                            var timeFiltersLen = 0;
                            var termFilterAndOr = self.termFilterAndOr;
                            var termFilterCombineWithPrev = self.termFilterCombineWithPrev;
                            var termFilterGroup = self.termFilterGroup;
                            _.each(self.termFilter,function (term, i) {
                                termFiltersLen += term.query.filter.terms().length;
                                termFilters.push(term.query.filter.terms());
                            })
                            _.each(self.timeFilter,function (timeFilter, i) {
                                timeFilters.push({
                                    year_min_max: timeFilter.query.filter.year_min_max(),
                                    filters: timeFilter.query.filter.filters(),
                                    inverted: timeFilter.query.filter.inverted()
                                });
                                timeFiltersLen += timeFilter.query.filter.year_min_max().length;
                                timeFiltersLen += timeFilter.query.filter.filters().length;
                            })
                        } else {
                            var termFilters = [self.termFilterSimple.query.filter.terms()];
                            var termFiltersLen = self.termFilterSimple.query.filter.terms().length;
                            var termFilterCombineWithPrev = [self.termFilterCombineWithPrev];
                            var termFilterAndOr = [self.termFilterAndOrSimple];
                            var termFilterGroup = [self.termFilterGroupSimple];
                            var timeFilters = [{
                                year_min_max: self.timeFilterSimple.query.filter.year_min_max(),
                                filters: self.timeFilterSimple.query.filter.filters(),
                                inverted: self.timeFilterSimple.query.filter.inverted()
                            }]
                            termFiltersLen = self.timeFilterSimple.query.filter.year_min_max().length;
                            timeFiltersLen += self.timeFilterSimple.query.filter.filters().length;
                        }
                        var params = {
                            page: self.searchResults.page(),
                            termFilter: ko.toJSON(termFilters),
                            temporalFilter: ko.toJSON(timeFilters),
                            spatialFilter: ko.toJSON(self.mapFilter.query.filter),
                            mapExpanded: self.mapFilter.expanded(),
                            timeExpanded: false,
                            booleanSearch: self.booleanSearch,
                            searchRelatedResources: self.searchRelatedResources,
                            termFilterAndOr: ko.toJSON(termFilterAndOr),
                            termFilterCombineWithPrev: ko.toJSON(termFilterCombineWithPrev),
                            termFilterGroup: ko.toJSON(termFilterGroup),
                            advancedSearch: self.advancedSearch ? "true" : "false",
                        };
                        
                        if (termFiltersLen === 0 &&
                            timeFiltersLen === 0 &&
                            self.mapFilter.query.filter.geometry.coordinates().length === 0) {
                            params.no_filters = true;
                        }

                        params.include_ids = self.isNewQuery;
                        return $.param(params).split('+').join('%20');
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.timeFilterSimple.query.changed());
                        _.each(self.timeFilter,function (timeFilter, i) {
                            ret = ret + ko.toJSON(timeFilter.query.changed());
                        })
                        ret = ret + ko.toJSON(this.termFilterSimple.query.changed());
                        _.each(self.termFilter,function (termFilter, i) {
                            ret = ret + ko.toJSON(termFilter.query.changed());
                        })
                        ret = ret + ko.toJSON(this.mapFilter.query.changed());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                };
                this.getSearchQuery();
                this.searchResults.page.subscribe(function(){
                    self.doQuery();
                });

                this.searchQuery.changed.subscribe(function(){
                    self.isNewQuery = true;
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

                $('.loading-mask').show();
                window.history.pushState({}, '', '?'+queryString);

                this.updateRequest = $.ajax({
                    type: "GET",
                    url: arches.urls.search_results,
                    data: queryString,
                    success: function(results){
                        var data = self.searchResults.updateResults(results);
                        self.mapFilter.highlightFeatures(data, $('.search-result-all-ids').data('results'));
                        self.mapFilter.applyBuffer();
                        self.isNewQuery = false;
                        $('.loading-mask').hide();
                    },
                    error: function(){}
                });
            },

            showSavedSearches: function(){
                this.clear();
                $('#saved-searches').slideDown('slow');
                $('#search-results').slideUp('slow');
                this.mapFilter.expanded(false);
                this.timeFilter.expanded(false);
            },

            hideSavedSearches: function(){
                $('#saved-searches').slideUp('slow');
                $('#search-results').slideDown('slow');
            },

            // clickMapFilter opens map filter if closed, toggles the invert map filter if open
            clickMapFilter: function () {
                if($('#saved-searches').is(":visible")){
                    this.isNewQuery = true;
                    this.doQuery();
                    this.hideSavedSearches();
                }
                if(this.mapFilter.expanded()){
                    if (this.mapFilter.inverted) {
                        this.mapFilter.inverted = false;
                        $("#map-filter-button").removeClass("inverted");
                    } else {
                        if (this.mapFilter.query.filter.geometry.coordinates().length > 0) {
                            this.mapFilter.inverted = true;
                            $("#map-filter-button").addClass("inverted");
                        } else {
                            this.closeMapFilter();
                        }
                    }
                    this.mapFilter.query.filter.inverted(this.mapFilter.inverted);
                } else {
                    this.mapFilter.expanded(true);
                    $("#map-filter-button").addClass("enabled");
                }
                window.history.pushState({}, '', '?'+this.searchQuery.queryString());
            },

            closeMapFilter: function (ev) {
                if($('#saved-searches').is(":visible")){
                    this.isNewQuery = true;
                    this.doQuery();
                    this.hideSavedSearches();
                }
                this.mapFilter.expanded(false);
                this.mapFilter.clear();
                
                $("#map-filter-button").removeClass("enabled");
                window.history.pushState({}, '', '?'+this.searchQuery.queryString());
                return false;
            },

            toggleTimeFilter: function(e){
                $(".time-filter-button").removeClass("btn-primary").addClass("btn-success");
                var i = $(e.target.closest(".search-box-container")).data("index");
                if($('#saved-searches').is(":visible")){
                    this.isNewQuery = true;
                    this.doQuery();
                    this.hideSavedSearches();
                }
                if (i == "_simple") {
                    this.timeFilterSimple.expanded(!this.timeFilterSimple.expanded());
                    _.each(this.timeFilter, function (timeFilter) {
                        timeFilter.expanded(false);
                    })
                    if (this.timeFilterSimple.expanded()) {
                        $(".search-box-container[data-index='" +i+ "'] .time-filter-button")
                            .removeClass("btn-success").addClass("btn-primary");
                    }
                } else {
                    this.timeFilterSimple.expanded(false);
                    _.each(this.timeFilter, function (timeFilter, j) {
                        if (i != j) {
                            timeFilter.expanded(false);
                        }
                    })
                    this.timeFilter[i].expanded(!this.timeFilter[i].expanded());
                    if (this.timeFilter[i].expanded()) {
                        $(".search-box-container[data-index='" +i+ "'] .time-filter-button")
                            .removeClass("btn-success").addClass("btn-primary");
                    }
                }
                window.history.pushState({}, '', '?'+this.searchQuery.queryString());
            },

            getQueryFromUrl: function (searchQuery) {
                var searchString = (searchQuery||searchQuery=='') ? searchQuery : location.search;
                return _.chain(decodeURIComponent(searchString).slice(1).split('&') )
                    // Split each array item into [key, value]
                    // ignore empty string if search is empty
                    .map(function(item) { if (item) return item.split('='); })
                    // Remove undefined in the case the search is empty
                    .compact()
                    // Turn [key, value] arrays into object parameters
                    .object()
                    // Return the value of the chain operation
                    .value();
            },

            getSearchQuery: function(searchQuery){
                var doQuery = false;
                var query = this.getQueryFromUrl(searchQuery);
                if('page' in query){
                    query.page = JSON.parse(query.page);
                    doQuery = true;
                }
                this.searchResults.restoreState(query.page);

                if('advancedSearch' in query){
                    var queryAdvancedSearch = query.advancedSearch == "true" ? true : false;
                    if (queryAdvancedSearch != this.advancedSearch) {
                        this.onToggleAdvancedSearch();
                    }
                    doQuery = true;
                }
                if (this.advancedSearch) {
                    this.showAdvancedSearch();
                } else {
                    this.hideAdvancedSearch();
                }
                
                var termsToRemove = [];
                if('termFilter' in query){
                    if (this.advancedSearch) {
                        query.termFilter = JSON.parse(query.termFilter);
                        // remove termfilters if they are empty
                        query.termFilter = _.filter(query.termFilter , function(filter, i){
                            if (i==0) return true;
                            if (filter.length == 0) {
                                termsToRemove.push(i);
                            }
                            return filter.length > 0
                         });
                        doQuery = true;
                        for (var i = 0; i < this.searchBoxes; i++) {
                            this.termFilter[i].restoreState(query.termFilter[i]);
                        }
                    } else {
                        query.termFilter = JSON.parse(query.termFilter);
                        doQuery = true;
                        this.termFilterSimple.restoreState(query.termFilter[0]);
                    }
                }

                if('temporalFilter' in query){
                    if (this.advancedSearch) {
                        query.temporalFilter = JSON.parse(query.temporalFilter);
                        // remove termfilters if they are empty
                        query.temporalFilter = _.filter(query.temporalFilter , function(filter, i){
                            if (termsToRemove.indexOf(i) < 0) {
                                return true;
                            } else {
                                return false;
                            }
                         });
                        doQuery = true;
                        for (var i = 0; i < this.searchBoxes; i++) {
                            this.timeFilter[i].restoreState(query.temporalFilter[i]);
                        }
                    } else {
                        query.temporalFilter = JSON.parse(query.temporalFilter);
                        doQuery = true;
                        this.timeFilterSimple.restoreState(query.temporalFilter[0]);
                    }
                }

                if('termFilterAndOr' in query){
                    var termFilterAndOr = _.filter(JSON.parse(query.termFilterAndOr) , function(filter, i){
                        if (termsToRemove.indexOf(i) < 0) {
                            return true;
                        } else {
                            return false;
                        }
                     });
                    _.each(termFilterAndOr, function (value ,i) {
                        if (i == 0) {
                            $(".select2-container.resource_search_widget_simple")
                                .closest(".search-box-container").find(".term-and-or-value").
                                html(value.charAt(0).toUpperCase() + value.slice(1));
                            this.termFilterAndOrSimple = value;
                        } else {
                            $(".select2-container.resource_search_widget"+i)
                                .closest(".search-box-container").find(".term-and-or-value").
                                html(value.charAt(0).toUpperCase() + value.slice(1));
                            this.termFilterAndOr[i] = value;
                        }
                    }.bind(this));
                    doQuery = true;
                }
                
                if('termFilterGroup' in query){
                    var termFilterGroup = _.filter(JSON.parse(query.termFilterGroup) , function(filter, i){
                        if (termsToRemove.indexOf(i) < 0) {
                            return true;
                        } else {
                            return false;
                        }
                     });
                    _.each(termFilterGroup, function (groupingValue ,i) {
                        if (!this.advancedSearch) {
                            var newValue = $($("a[data-value='" + groupingValue + "']")[0]).html();
                            $(".select2-container.resource_search_widget_simple")
                                .closest(".search-box-container").find(".term-group-value").
                                html(newValue);
                            this.termFilterGroupSimple = groupingValue;
                            this.termFilterSimple.termFilterGroup = groupingValue;
                        } else {
                            var newValue = $($("a[data-value='" + groupingValue + "']")[i]).html();
                            $(".select2-container.resource_search_widget"+i)
                                .closest(".search-box-container").find(".term-group-value").
                                html(newValue);
                            this.termFilterGroup[i] = groupingValue;
                            this.termFilter[i].termFilterGroup = groupingValue;
                        }
                        var index = (i == 0) ? "_simple" : i;
                        if (groupingValue != "No group") {
                            $(".search-box-container[data-index='"+index+"'] .term-and-or").hide();
                        } else {
                            $(".search-box-container[data-index='"+index+"'] .term-and-or").show();
                        }

                    }.bind(this));
                    doQuery = true;
                }

                if('booleanSearch' in query){
                    this.onChangeAndOr(query.booleanSearch);
                    doQuery = true;
                }
                if('searchRelatedResources' in query){
                    this.onChangeRelatedResources(query.searchRelatedResources);
                    doQuery = true;
                }

                if('termFilterCombineWithPrev' in query){
                    var termFilterCombineWithPrev = _.filter(JSON.parse(query.termFilterCombineWithPrev) , function(filter, i){
                        if (termsToRemove.indexOf(i) < 0) {
                            return true;
                        } else {
                            return false;
                        }
                     });
                    _.each(termFilterCombineWithPrev, function (value ,i) {
                        if (i == 0) {
                            this.termFilterCombineWithPrevSimple = [false];
                        } else {
                            this.termFilterCombineWithPrev[i] = value;
                            $(".select2-container.resource_search_widget"+i)
                                .closest(".search-box-container").find(".toggle-combine-prev")
                                .removeClass(this.termFilterCombineWithPrev[i] ? 'toggle-combine-off' : 'toggle-combine-on btn-success')
                                .addClass(!this.termFilterCombineWithPrev[i] ? 'toggle-combine-off' : 'toggle-combine-on btn-success')
                            if (this.termFilterCombineWithPrev[i]) {
                                $(".search-box-container[data-index='"+ parseInt(i-1) +"']").addClass('prev-combine-box')
                            } else {
                                $(".search-box-container[data-index='"+ parseInt(i-1) +"']").removeClass('prev-combine-box')
                            }

                        }
                    }.bind(this));
                    doQuery = true;
                }
                if('timeExpanded' in query){
                    query.timeExpanded = JSON.parse(query.timeExpanded);
                    doQuery = true;
                }

                if('spatialFilter' in query){
                    query.spatialFilter = JSON.parse(query.spatialFilter);
                    doQuery = true;
                }
                if('mapExpanded' in query){
                    query.mapExpanded = JSON.parse(query.mapExpanded);
                    doQuery = true;
                }
                this.mapFilter.restoreState(query.spatialFilter, query.mapExpanded);
                

                if(doQuery){
                    this.isNewQuery = true;
                    this.doQuery();
                    this.hideSavedSearches();
                }
                
            },

            clear: function(){
                this.mapFilter.clear();
                this.timeFilterSimple.clear();
                this.termFilterSimple.clear();
                for (var i = 0; i < this.searchBoxes; i++) {
                    this.termFilter[i].clear();
                    this.timeFilter[i].clear();
                }
            },

            exportSearch: function(e) {
                var export_format = e.currentTarget.id,
                    _href = $("a.dataexport").attr("href"),
                    format = 'export=' + export_format,
                    params_with_page = this.searchQuery.queryString(),
                    page_number_regex = /page=[0-9]+/;
                    params = params_with_page.replace(page_number_regex, format);
                $("a.dataexport").attr("href", arches.urls.search_results_export + '?' + params);
            },
            
            onChangeAndOr: function (e) {
                var targetClass;
                if (e.target) {
                    if ($(e.target).hasClass("search-and")) {
                        targetClass = "and";
                    }
                    if ($(e.target).hasClass("search-or")) {
                        targetClass = "or";
                    }
                } else {
                    targetClass = e;
                }
                if (targetClass == 'and') {
                    if (this.booleanSearch != "and") {
                        $(".and-or-value").html("And");
                        this.booleanSearch = "and";
                        $(".select2-choices").removeClass("or-search");
                        this.isNewQuery = true;
                        this.doQuery();
                    }
                } else if (targetClass == 'or') {
                    if (this.booleanSearch != "or") {
                        $(".and-or-value").html("Or");
                        this.booleanSearch = "or";
                        $(".select2-choices").addClass("or-search");
                        this.isNewQuery = true;
                        this.doQuery();
                    }
                }

            },
            
            onClickRelatedResources: function () {
                this.searchRelatedResources = true;
                var relatedQuery = this.searchQuery.queryString();
                this.searchRelatedResources = false;
                window.open('search?page=1&searchRelatedResources=true','_blank');
            },
            
            onChangeRelatedResources: function (e) {
                    if (e == 'true') {
                        this.searchRelatedResources = true;
                        $('.toggle-related-resources')
                            .removeClass('toggle-related-off').addClass('disabled');
                    }
                    this.isNewQuery = true;
                    this.doQuery();
            },
            
            onToggleAdvancedSearch: function () {
                if (this.advancedSearch) {
                    this.advancedSearch = false;
                    this.hideAdvancedSearch();
                } else {
                    this.advancedSearch = true;
                    this.showAdvancedSearch();
                }
                this.timeFilterSimple.expanded(false);
                _.each(this.timeFilter, function (timeFilter, j) {
                    timeFilter.expanded(false);
                })
                $(".time-filter-button").removeClass("btn-primary").addClass("btn-success");
                this.isNewQuery = true;
                this.doQuery();
            },
            
            showAdvancedSearch: function () {
                $(".btn.advanced-search").addClass("btn-primary");
                // $(".select2-container.select-location-time").show();
                $(".search-box-container.term-search-advanced").show();
                $(".search-box-container.term-search-simple").hide();
                $(".global-and-or").show();
                $(".add-remove-search-box").show();
            },
            hideAdvancedSearch: function () {
                $(".btn.advanced-search").removeClass("btn-primary");
                // $(".select2-container.select-location-time").hide();
                $(".search-box-container.term-search-advanced").hide();
                $(".search-box-container.term-search-simple").show();
                $(".global-and-or").hide();
                $(".add-remove-search-box").hide();
            },
            
            onChangeTermAndOr: function (e) {
                var i = $(e.target.closest("div")).data("index");
                if (i == "_simple") {
                    var termFilterAndOr = this.termFilterAndOrSimple
                } else {
                    var termFilterAndOr = this.termFilterAndOr[i]
                }
                var newValue = $(e.target).html();
                var oldValue = $(e.target).closest(".dropdown").find(".term-and-or-value").html();
                if (newValue != oldValue) {
                    $(e.target).closest(".dropdown").find(".term-and-or-value").html(newValue);
                    if (i == "_simple") {
                        this.termFilterAndOrSimple = e.target.dataset.value;
                        this.termFilterSimple.termFilterGroup = "No group";
                    } else {
                        this.termFilterAndOr[i] = e.target.dataset.value;
                        this.termFilter[i].termFilterGroup = "No group";
                    }
                    this.isNewQuery = true;
                    this.doQuery();
                }
            },
            onChangeCombineWithPrev: function (e) {
                var i = $(e.target.closest("div")).data("index");
                if (i != "_simple") {
                    this.termFilterCombineWithPrev[i] = this.termFilterCombineWithPrev[i] ? false : true;
                    $(".select2-container.resource_search_widget"+i)
                        .closest(".search-box-container").find(".toggle-combine-prev")
                        .removeClass(this.termFilterCombineWithPrev[i] ? 'toggle-combine-off' : 'toggle-combine-on btn-success')
                        .addClass(!this.termFilterCombineWithPrev[i] ? 'toggle-combine-off' : 'toggle-combine-on btn-success')
                    if (this.termFilterCombineWithPrev[i]) {
                        $(".search-box-container[data-index='"+ parseInt(i-1) +"']").addClass('prev-combine-box')
                    } else {
                        $(".search-box-container[data-index='"+ parseInt(i-1) +"']").removeClass('prev-combine-box')
                    }
                    this.isNewQuery = true;
                    this.doQuery();
                }
            },

            onChangeGroup: function (e) {
                var i = $(e.target.closest("div")).data("index");
                if (i == "_simple") {
                    var termFilterGroup = this.termFilterGroupSimple
                } else {
                    var termFilterGroup = this.termFilterGroup[i]
                }
                var newValue = $(e.target).html();
                var oldValue = $(e.target).closest(".dropdown").find(".term-group-value").html();
                if (newValue != oldValue) {
                    $(e.target).closest(".dropdown").find(".term-group-value").html(newValue);
                    if (newValue != "No group") {
                        $(".search-box-container[data-index='"+i+"'] .term-and-or").hide();
                    } else {
                        $(".search-box-container[data-index='"+i+"'] .term-and-or").show();
                    }
                    if (i == "_simple") {
                        this.termFilterSimple.clear();
                        this.termFilterGroupSimple = e.target.dataset.value;
                        this.termFilterSimple.termFilterGroup = e.target.dataset.value;
                    } else {
                        this.termFilter[i].clear();
                        this.termFilterGroup[i] = e.target.dataset.value;
                        this.termFilter[i].termFilterGroup = e.target.dataset.value;
                    }
                    this.isNewQuery = true;
                    this.doQuery();
                }
            },

            initializeSearchBoxes: function () {
                this.termFilter = [];
                this.timeFilter = [];
                this.termFilterAndOr = [];
                this.termFilterCombineWithPrev = [];
                this.termFilterGroup = [];
                this.cloneSearchBox("_simple");
                this.cloneTimeFilter("_simple");
                this.termFilterAndOrSimple = "and";
                this.termFilterCombineWithPrevSimple = false;
                this.termFilterGroupSimple = "No group";
                this.termFilterSimple = this.addSearchBox("_simple");
                this.timeFilterSimple = this.addTimeFilter("_simple");
                this.addSearchBoxEvents(this.termFilterSimple, "_simple");
                $(".search-box-container[data-index='_simple']").addClass("term-search-simple");
                for (var i = 0; i < this.searchBoxes; i++) {
                    this.cloneSearchBox(i);
                    this.cloneTimeFilter(i);
                    this.termFilterAndOr[i] = "and";
                    this.termFilterCombineWithPrev[i] = false;
                    this.termFilterGroup[i] = "No group";
                    this.termFilter[i] = this.addSearchBox(i);
                    this.timeFilter[i] = this.addTimeFilter(i);
                    this.addSearchBoxEvents(this.termFilter[i], i);
                    $(".search-box-container[data-index='"+i+"']").addClass("term-search-advanced");
                }
                if (this.searchBoxes == 1) {
                    $(".remove-search-box").addClass("disabled");
                }
                $(".search-box-container[data-index='0'] .toggle-combine-prev").hide();
                $(".search-box-container[data-index='_simple'] .toggle-combine-prev").hide();
            },
            
            addSearchBox: function (i) {
                var newTermFilter = new TermFilter({
                    el: $.find('input.resource_search_widget' + i)[0],
                    termFilterAndOr: "And",
                    termFilterCombineWithPrev: false,
                    termFilterGroup: "No group",
                    index: i
                });
                return newTermFilter;
            },

            addTimeFilter: function (i) {
                var newTimeFilter = new TimeFilter({
                    el: $(".time-filters [data-index='"+ i +"'] .arches-time-filter"),
                    index: i
                });
                return newTimeFilter;
            },
            
            addSearchBoxEvents: function (termFilter, i) {
                termFilter.on('change', function(){
                    this.isNewQuery = true;
                    this.searchResults.page(1);
                    _.defer(function () {
                        this.doQuery();
                    }.bind(this)) 
                    if($('#saved-searches').is(":visible")){
                        this.hideSavedSearches();
                    }
                }, this);
                var timeFilter = this.getTimeFilter(i);
                termFilter.on('filter-removed', function(item){
                    if(item.text === this.mapFilterText){
                        this.mapFilter.clear();
                    }
                    if(item.text === this.timeFilterText){
                        timeFilter.clear();
                    }
                }, this);
                termFilter.on('filter-inverted', function(item){
                    if(item.text === this.mapFilterText){
                        this.mapFilter.query.filter.inverted(item.inverted);
                    }
                    if(item.text === this.timeFilterText){
                        timeFilter.query.filter.inverted(item.inverted);
                    }
                }, this);
                timeFilter.on('enabled', function(enabled, inverted){
                    if(enabled){
                        termFilter.addTag(this.timeFilterText, inverted);
                    }else{
                        termFilter.removeTag(this.timeFilterText);
                    }
                }, this);
                timeFilter.on('change', function(){
                    this.isNewQuery = true;
                    this.searchResults.page(1);
                    _.defer(function () {
                        this.doQuery();
                    }.bind(this)) 
                    if($('#saved-searches').is(":visible")){
                        this.hideSavedSearches();
                    }
                }, this);

            },

            getTimeFilter: function (i) {
                var timeFilter = this.timeFilterSimple;
                if (i != "_simple") {
                    timeFilter = this.timeFilter[i];
                }
                return timeFilter;
            },
            
            cloneSearchBox: function (i) {
                var cloneInput = $("#term-select-template").clone()
                    .removeAttr('id','term-select-template')
                    .removeClass('hidden')
                    .attr('data-index', i);
                cloneInput.find(".arches-select2").addClass('resource_search_widget' + i);
                $(".term-search-boxes").append(cloneInput);
            },

            cloneTimeFilter: function (i) {
                var cloneInput = $("#time-filter-container-template").clone()
                    .removeAttr('id','time-filter-container-template')
                    .removeClass('hidden')
                    .attr('data-index', i);
                cloneInput.find(".arches-time-filter").addClass('resource_time_filter_widget' + i);
                $(".time-filters").append(cloneInput);
            },

            removeSearchBox: function (i) {
                $('.resource_search_widget' + i).remove();
                this.termFilter[i].stopListening();
                this.termFilter[i].remove();
                this.termFilter.splice(i, 1);
                this.termFilterAndOr.splice(i, 1);
                this.termFilterCombineWithPrev.splice(i, 1);
                this.termFilterGroup.splice(i, 1);
                this.timeFilter[i].stopListening();
                this.timeFilter[i].remove();
                this.timeFilter.splice(i, 1);
                this.isNewQuery = true;
                this.doQuery();
            },
            
            onAddSearchBox: function (e) {
                $(".remove-search-box").removeClass("disabled");
                this.cloneSearchBox(this.searchBoxes);
                this.cloneTimeFilter(this.searchBoxes);
                this.termFilterAndOr[this.searchBoxes] = "and";
                this.termFilterCombineWithPrev[this.searchBoxes] = false;
                this.termFilterGroup[this.searchBoxes] = "No group";
                this.termFilter[this.searchBoxes] = this.addSearchBox(this.searchBoxes);
                this.timeFilter[this.searchBoxes] = this.addTimeFilter(this.searchBoxes);
                this.addSearchBoxEvents (this.termFilter[this.searchBoxes], this.searchBoxes);
                $(".search-box-container[data-index='"+this.searchBoxes+"']").addClass("term-search-advanced");
                this.searchBoxes++;
            },

            onRemoveSearchBox: function (e) {
                if (this.searchBoxes > 1) {
                    this.searchBoxes--;
                    this.removeSearchBox(this.searchBoxes);
                    $(".search-box-container[data-index="+ this.searchBoxes +"]").remove();
                    if (this.searchBoxes == 1) {
                        $(".remove-search-box").addClass("disabled");
                    }
                }
            },
        });
        new SearchView();
    });
});