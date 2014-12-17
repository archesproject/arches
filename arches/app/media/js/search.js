require(['jquery', 
    'backbone',
    'arches', 
    'views/resource-search', 
    'openlayers', 
    'knockout', 
    'knockout-mapping'], 
    function($, Backbone, arches, ResourceSearch, ol, ko, koMapping) {
    $(document).ready(function() {
        var SearchResultsView = Backbone.View.extend({
            el: $('body'),
            updateRequest: '',
            // searchQuery: {
            //     page: 1
            // },

            events: {
                'click .page-button': 'newPage',
                'click #view-saved-searches': 'showSavedSearches',
                'click #map-filter-button': 'toggleMapFilter',
                'click #time-filter-button': 'toggleTimeFilter',
                'click .layer-zoom': 'layerZoom'
            },

            initialize: function(options) { 
                var self = this;
                this.searchQuery = {
                    page: ko.observable(),
                    // q: {
                    //     strings: ko.observableArray(),
                    //     concepts: ko.observableArray()
                    // },
                    q: ko.observableArray(),
                    date: ko.observable(),
                    geo: ko.observable(),
                    queryString: ko.pureComputed(function(){
                        var q = [];
                        var page, date, geo;

                        // if (self.searchQuery.q()){
                        //     $.each(self.searchQuery.q(), function(){
                        //         q.push(this);
                        //     })                            
                        // }

                        var params = {
                            page: self.searchQuery.page(),
                            q: JSON.stringify(self.searchQuery.q()),
                            date: self.searchQuery.date(),
                            geo: self.searchQuery.geo()
                        }; 
                        return $.param(params);
                    })
                }

                this.searchQuery.queryString.subscribe(function(querystring){
                    console.log(querystring);
                    self.updateResults();
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

                this.searchRestulsViewModel = {
                    total: ko.observable(),
                    results: ko.observableArray()
                };
                ko.applyBindings(this.searchRestulsViewModel, $('#search-results')[0]);

                this.termFilterViewModel = {
                    filters: ko.observableArray()
                };
                this.termFilterViewModel.filters.subscribe(function(){
                    console.log(arguments);
                });
                //ko.applyBindings(this.termFilterViewModel, $('#map-filter')[0]);

                this.mapFilterViewModel = {
                    filters: ko.observableArray()
                };
                ko.applyBindings(this.mapFilterViewModel, $('#map-filter')[0]);

                this.timeFilterViewModel = {
                    filters: ko.observableArray()
                };
                ko.applyBindings(this.timeFilterViewModel, $('#time-filter')[0]);


                this.getSearchQuery();


                function handleMapPanel() {    
                    //function to toggle display of wizard div
                    $( "#map" ).slideToggle(600);

                    var projection = ol.proj.get('EPSG:3857');

                    var styleFunction = function(feature, resolution) {
                        var featureStyleFunction = feature.getStyleFunction();
                        if (featureStyleFunction) {
                            return featureStyleFunction.call(feature, resolution);
                        } else {
                            return defaultStyle[feature.getGeometry().getType()];
                        }
                    };

                    var dragAndDropInteraction = new ol.interaction.DragAndDrop({
                        formatConstructors: [
                            ol.format.GPX,
                            ol.format.GeoJSON,
                            ol.format.IGC,
                            ol.format.KML,
                            ol.format.TopoJSON
                        ]
                    });

                    dragAndDropInteraction.on('addfeatures', function(event) {
                        var vectorSource = new ol.source.Vector({
                            features: event.features,
                            projection: event.projection
                        });
                        map.getLayers().push(new ol.layer.Vector({
                            source: vectorSource,
                            style: styleFunction
                        }));
                        var view = map.getView();
                        view.fitExtent(
                            vectorSource.getExtent(), /** @type {ol.Size} */ 
                            map.getSize()
                        );
                    });

                    var gmap = new google.maps.Map(document.getElementById('searchmap'), {
                        disableDefaultUI: true,
                        keyboardShortcuts: false,
                        draggable: false,
                        disableDoubleClickZoom: true,
                        scrollwheel: false,
                        streetViewControl: false
                    });

                    var view = new ol.View({
                        // make sure the view doesn't go beyond the 22 zoom levels of Google Maps
                        maxZoom: 21
                    });

                    view.on('change:center', function() {
                          var center = ol.proj.transform(view.getCenter(), 'EPSG:3857', 'EPSG:4326');
                          gmap.setCenter(new google.maps.LatLng(center[1], center[0]));
                    });

                    view.on('change:resolution', function() {
                        gmap.setZoom(view.getZoom());
                    });

                    //Add kml file to mockup CH spatial data
                    var vector = new ol.layer.Vector({
                        source: new ol.source.KML({
                            projection: projection,
                            url: 'data/test_v2.kml'
                        })
                    });

                    //Show Name of kml features
                    var displayFeatureInfo = function(pixel) {
                        var features = [];
                        
                        map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                            features.push(feature);
                        });

                        if (features.length > 0) {
                            var info = [];
                            var i, ii;
                        
                            for (i = 0, ii = features.length; i < ii; ++i) {
                              info.push(features[i].get('name'));
                            }
                        
                            document.getElementById('info').innerHTML = info.join(', ') || '(unknown)';
                            map.getTarget().style.cursor = 'pointer';

                        } else {

                            document.getElementById('info').innerHTML = '&nbsp;';
                            map.getTarget().style.cursor = '';

                        }
                    };


                    //Map display options
                    var olMapDiv = document.getElementById('olmap');
                    var map = new ol.Map({
                        layers: [vector],
                        interactions: ol.interaction.defaults({
                            altShiftDragRotate: false,
                            dragPan: false,
                            rotate: false
                        }).extend([new ol.interaction.DragPan({kinetic: null})]).extend([dragAndDropInteraction]),
                        target: olMapDiv,
                        view: view
                    });
                    

                    view.setCenter([-13172009.0, 4013435.2]);
                    view.setZoom(13);


                    $(map.getViewport()).on('mousemove', function(evt) {
                    

                    //Track cursor, setup click event on KML marker
                    var pixel = map.getEventPixel(evt.originalEvent);
                        displayFeatureInfo(pixel);
                    });

                    map.on('click', function(evt) {
                        displayFeatureInfo(evt.pixel);
                    });


                    //OL Map Controls
                    olMapDiv.parentNode.removeChild(olMapDiv);
                    gmap.controls[google.maps.ControlPosition.TOP_LEFT].push(olMapDiv);


                    var interval = setInterval(function(){ startTimer();}, 1000);

                    //Hack to get kml to show on map in bootstrap modal
                    //see http://stackoverflow.com/questions/22699552/cant-get-openlayers-3-map-to-display-in-bootstrap-modal
                    var startTimer = function  () {
                        map.updateSize();
                    }

                    map.on('click', function(event) {
                      clearInterval(interval);
                    });


                }

                function handleTimePanel() {    
                    
                    //function to toggle display of wizard div
                    $( "#searchtime" ).slideToggle(600);

                }
            },

            newPage: function(evt){
                var data = $(arguments[0].target).data();
                this.searchQuery.page(data.page);
            },

            updateResults: function () {
                var self = this;
                this.toggleLoading('show');
                if (this.updateRequest) {
                    this.updateRequest.abort();
                    this.toggleLoading('hide');
                }
                this.updateRequest = $.ajax({
                    type: "GET",
                    url: arches.urls.search_results,
                    data: this.searchQuery.queryString(),
                    success: function(results){
                        $('#paginator').html(results);
                        self.bind(results);
                        self.toggleLoading('hide');
                        self.toggleSearchResults('show');
                        self.toggleSavedSearches('hide');
                    },
                    error: function(){
                        self.toggleLoading('hide');
                    }
                });
            },

            bind: function(results){
                var self = this;
                var data = $('div[name="search-result-data"]').data();
                //koMapping.fromJS(data.hits.hits);
                this.searchRestulsViewModel.total(data.results.hits.total);
                self.searchRestulsViewModel.results.removeAll();
                $.each(data.results.hits.hits, function(){
                    //var data = koMapping.fromJS(this);;
                    self.searchRestulsViewModel.results.push({
                        primaryname: this._source.primaryname,
                        entityid: this._source.entityid,
                        entitytypeid: this._source.entitytypeid,
                        descritption: '',
                        geometries: ko.observableArray(this._source.geometries)
                    });
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
                var ele = $('#search-results-list');
                this.slideToggle(ele, showOrHide);
            },

            toggleLoading: function(showOrHide){
                // var ele = $('#search-results-loading');
                // this.slideToggle(ele, showOrHide);
            },

            toggleMapFilter: function(showOrHide){
                var ele = $('#map-filter');
                this.slideToggle(ele);
                this.hideSavedSearches();
            },

            toggleTimeFilter: function(showOrHide){
                var ele = $('#time-filter');
                this.slideToggle(ele);
                this.hideSavedSearches();
            },

            slideToggle: function(ele, showOrHide){
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

            setMapFilter: function(query){
                
            },

            setTimeFilter: function(query){
                
            },

            getSearchQuery: function(){
                var query = _.chain( location.search.slice(1).split('&') )
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
                    this.searchQuery.page(query.page);
                }
                if(query.q){
                    this.searchQuery.q(query.q);
                }
                if(query.date){
                    this.searchQuery.date(query.date);
                }
                if(query.geo){
                    this.searchQuery.geo(query.geo);
                }
                

                window.onpopstate = function(event) {
                  //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
                    //window.location = document.location;
                };
            },

            setSearchQuery: function(){

            },


        });



        new SearchResultsView();

    });
});