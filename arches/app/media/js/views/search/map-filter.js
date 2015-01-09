define(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'views/map',
    'openlayers', 
    'knockout',
    'resource-types'], 
    function($, _, Backbone, bootstrap, arches, MapView, ol, ko, resourceTypes) {
        return Backbone.View.extend({

            events: {
                'click .layer-zoom': 'layerZoom',
                'click #map-extent-filter': 'applyfilter',
                'click #polygon-filter': 'applyfilter',
                'click #point-filter': 'applyfilter',
                'click #line-filter': 'applyfilter',
                'click #map-tools-dropdown': 'handleMapToolsBtn'
            },

            initialize: function(options) { 
                var self = this;

                this.expanded = ko.observable(false);
                this.expanded.subscribe(function(status){
                    self.toggleFilterSection($('#map-filter'), status)
                });

                this.query = {
                    filter: {
                        geometry:{
                            type: ko.observable(''),
                            coordinates: ko.observable([])
                        },
                        buffer: {
                            width: ko.observable('0'),
                            unit: ko.observable('ft')
                        }
                    },
                    queryString: function(){
                        var params = {
                            filter: ko.toJSON(this.filter),
                            expanded: this.expanded
                        }; 
                        return $.param(params);
                    }, 
                    isEmpty: function(){
                        if (self.query.filter.geometry.type() === ''){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        return ko.toJSON(this.query.filter.geometry.coordinates());
                    }, this).extend({ rateLimit: 200 })
                }

                ko.applyBindings(this.query.filter, $('#map-tools-dropdown')[0]); 

                this.query.filter.buffer.width.subscribe(function(){
                    self.applyBuffer();
                });

                this.addResourceLayer();
            },

            addResourceLayer: function(){

                var style = new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: '#9E9E9E'
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#9E9E9E',
                        width: 1
                    }),
                    image: new ol.style.Circle({
                        radius: 5,
                        stroke: new ol.style.Stroke({
                            color: '#fff'
                        }),
                        fill: new ol.style.Fill({
                            color: '#9E9E9E'
                        })
                    })
                });

                this.vectorLayer = new ol.layer.Vector({
                    //maxResolution: arches.mapDefaults.cluster_min,
                    source: new ol.source.GeoJSON({
                        projection: 'EPSG:3857',
                        url: 'resources/layers/'
                    }),
                    style: style
                });

                this.map = new MapView({
                    el: $('#map'),
                    overlays: [this.vectorLayer]
                });

                var highlightStyleCache = {};
                this.featureOverlay = new ol.FeatureOverlay({
                    map: this.map.map,
                    style: function(feature, resolution) {
                        var text = resolution < 5000 ? feature.get('primaryname') : '';
                        if (!highlightStyleCache[text]) {
                            highlightStyleCache[text] = [
                                new ol.style.Style({
                                    fill: new ol.style.Fill({
                                        color: '#00C819'
                                    }),
                                    stroke: new ol.style.Stroke({
                                        color: '#00C819',
                                        width: 1
                                    }),
                                    image: new ol.style.Circle({
                                        radius: 5,
                                        stroke: new ol.style.Stroke({
                                            color: '#fff'
                                        }),
                                        fill: new ol.style.Fill({
                                            color: '#00C819'
                                        })
                                    }),
                                    text: new ol.style.Text({
                                        font: '12px Calibri,sans-serif',
                                        text: text,
                                        offsetY: -12,
                                        fill: new ol.style.Fill({
                                            color: '#fff',
                                            width: 4
                                        }),
                                        stroke: new ol.style.Stroke({
                                            color: '#006E2B',
                                            width: 4
                                        })
                                    })
                                })
                            ];
                        }
                        return highlightStyleCache[text];
                    }
                });

                function zoomToLayer(vectorLayer, map){
                    var extent = (vectorLayer.getSource().getExtent());
                    var size = (map.map.getSize());
                    var view = map.map.getView()
                    view.fitExtent(
                        extent,
                        size
                    );
                }

                zoomToLayer(this.vectorLayer, this.map)

            },

            highlightFeatures: function(resultsarray){
                this.featureOverlay.getFeatures().clear();
                _.each(resultsarray, function(result){
                    var feature = this.vectorLayer.getSource().getFeatureById(result.resourceid);
                    if(feature){
                        this.featureOverlay.addFeature(feature);
                    }
                }, this);
            },

            getMapExtent: function(){
                var extent = ol.proj.transformExtent(this.map.map.getView().calculateExtent(this.map.map.getSize()), 'EPSG:3857', 'EPSG:4326');
                return extent;
            },

            onMoveEnd: function(evt) {
                this.query.filter.geometry.coordinates(this.getMapExtent());
            },

            applyfilter: function(evt){
                var link = $(evt.target).closest('a');
                var data = link.data();
                var item = link.find('i');

                this.disableDrawingTools();
                
                if (!(item.hasClass("fa-check"))){
                    //User is adding filter

                    if(data.tooltype){
                        if(data.tooltype === 'map-extent'){
                            this.query.filter.geometry.type('bbox');
                            this.query.filter.geometry.coordinates(this.getMapExtent());
                            this.map.map.on('moveend', this.onMoveEnd, this);
                        }else{
                            this.query.filter.geometry.type(data.tooltype);
                            this.enableDrawingTools(this.map.map, data.tooltype);
                            this.map.map.un('moveend', this.onMoveEnd, this);     
                        }                  
                    }

                }else{
                    //User is removing filter
                    if(data.tooltype){
                        this.query.filter.geometry.type('');
                        this.query.filter.geometry.coordinates([]);

                        if(data.tooltype === 'map-extent'){
                            this.map.map.un('moveend', this.onMoveEnd, this);
                        } 
                    }
                }
            },

            enableDrawingTools: function(map, tooltype){
                if (!this.bufferFeatureOverlay){
                    this.bufferFeatureOverlay = new ol.FeatureOverlay({
                        style: new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgba(123, 123, 255, 0.5)'
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#ff6633',
                                width: 2,
                                lineDash: [4,4]
                            })
                        })
                    }); 
                    this.bufferFeatureOverlay.setMap(map);                   
                }
                
                if (!this.drawingFeatureOverlay){
                    this.drawingFeatureOverlay = new ol.FeatureOverlay({
                        style: new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgba(255, 255, 255, 0.2)'
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#ffcc33',
                                width: 2
                            })
                        })
                    });
                    this.drawingFeatureOverlay.setMap(map);
                }

                var modify = new ol.interaction.Modify({
                    features: this.drawingFeatureOverlay.getFeatures(),
                    // the SHIFT key must be pressed to delete vertices, so
                    // that new vertices can be drawn at the same position
                    // of existing vertices
                    deleteCondition: function(event) {
                        return ol.events.condition.shiftKeyOnly(event) &&
                                ol.events.condition.singleClick(event);
                    }
                });
                map.addInteraction(modify);

                this.drawingtool = new ol.interaction.Draw({
                    features: this.drawingFeatureOverlay.getFeatures(),
                    type: tooltype
                });

                this.drawingtool.on('drawstart', function(){
                    if(this.drawingtool.o !== 'Point'){
                        this.clearDrawingFeatures();                       
                    }
                }, this);

                this.drawingtool.on('drawend', function(evt){
                    var self = this;
                    var geometry = evt.feature.getGeometry().clone();
                    geometry.transform('EPSG:3857', 'EPSG:4326');
                    this.query.filter.geometry.coordinates(geometry.getCoordinates());

                    //this.applyBuffer();
                    
                    evt.feature.on('change', function(evt) {
                        var geometry = evt.target.getGeometry().clone();
                        geometry.transform('EPSG:3857', 'EPSG:4326');
                        self.query.filter.geometry.coordinates(geometry.getCoordinates());
                        //self.applyBuffer();
                    });
                }, this);

                map.addInteraction(this.drawingtool);
            },

            disableDrawingTools: function(){
                if(this.drawingtool){
                    this.map.map.removeInteraction(this.drawingtool);
                    this.clearDrawingFeatures();
                }
            },

            clearDrawingFeatures: function(){
                if (this.bufferFeatureOverlay){
                    this.bufferFeatureOverlay.getFeatures().clear();                 
                }
                
                if (this.drawingFeatureOverlay){
                    this.drawingFeatureOverlay.getFeatures().clear();
                }
            },

            applyBuffer: function(){
                var self = this;
                if(this.query.filter.buffer.width() > 0 && this.drawingFeatureOverlay.getFeatures().getLength() > 0){
                    $.ajax({
                        type: "GET",
                        url: arches.urls.buffer,
                        data: this.query.queryString(),
                        success: function(results){
                            var source = new ol.source.GeoJSON(({object:{type: 'FeatureCollection', features: [{type:'Feature', geometry: JSON.parse(results)}]}}));
                            var feature = source.getFeatures()[0];
                            feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
                            self.bufferFeatureOverlay.getFeatures().clear();  
                            self.bufferFeatureOverlay.addFeature(feature);
                        },
                        error: function(){}
                    });                    
                }
            },

            toggleFilterSection: function(ele, expand){
                if(expand){
                    this.slideToggle(ele, 'show');
                }else{
                    this.slideToggle(ele, 'hide');               
                }
            },

            slideToggle: function(ele, showOrHide){
                var self = this;
                if ($(ele).is(":visible") && showOrHide === 'hide'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!($(ele).is(":visible")) && showOrHide === 'show'){
                    ele.slideToggle('slow', function(){
                        self.map.map.updateSize();
                    });
                    return;
                }

                if (!showOrHide){
                    ele.slideToggle('slow');                    
                }
            },

            handleMapToolsBtn: function(evt){
                evt.stopPropagation();
            }


        });
});