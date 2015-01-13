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
                'click .layer-zoom': 'layerZoom'
            },

            initialize: function(options) { 
                var self = this;
                x = this;

               //  Handle show/hide toggle ourselves
                $('#map-tools-btn').on('click', function(evt) {
                    if($(evt.currentTarget).hasClass('open')){
                        self.disableDrawingTools();
                    }
                    else {
                        self.enableDrawingTools();
                    }
                    $(evt.currentTarget).toggleClass('open');
                    return false;
                });
                $('#map-tools-dropdown').on('click', 'a', function(evt) {
                    if($(evt.target).attr('name') === 'map-tools'){
                        self.applyfilter(evt);
                    }
                    return false;
                });

                //  suppress default bahavior of the bootstrap menu to auto close
                $('#map-tools-btn').on('hide.bs.dropdown', false);            
                $('#map-tools-btn').on('show.bs.dropdown', false);

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
                    isEmpty: function(){
                        if (this.filter.geometry.type() === ''){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        return (ko.toJSON(this.query.filter.geometry.coordinates()) + 
                            ko.toJSON(this.query.filter.buffer.width()));
                    }, this).extend({ rateLimit: 200 })
                }

                ko.applyBindings(this.query.filter, $('#map-tools-dropdown')[0]); 

                this.query.filter.buffer.width.subscribe(function(){
                    self.applyBuffer();
                });

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
                this.bufferFeatureOverlay.setMap(this.map.map);                   
                
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
                this.drawingFeatureOverlay.setMap(this.map.map);

                this.zoomToExtent(this.vectorLayer.getSource().getExtent())

            },

            zoomToExtent: function(extent){
                var size = this.map.map.getSize();
                var view = this.map.map.getView()
                view.fitExtent(
                    extent,
                    size
                );
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

                this.clearDrawingFeatures();
 
                if (!(item.hasClass("fa-check"))){
                    //User is adding filter

                    if(data.tooltype){
                        if(data.tooltype === 'map-extent'){
                            this.removeDrawingTools();
                            this.query.filter.geometry.type('bbox');
                            this.query.filter.geometry.coordinates(this.getMapExtent());
                            this.map.map.on('moveend', this.onMoveEnd, this);
                        }else{
                            this.query.filter.geometry.type(data.tooltype);
                            this.changeDrawingTool(this.map.map, data.tooltype);
                            this.map.map.un('moveend', this.onMoveEnd, this);     
                        }                  
                    }

                }else{
                    //User is removing filter
                    if(data.tooltype){
                        this.removeDrawingTools();
                        this.query.filter.geometry.type('');
                        this.query.filter.geometry.coordinates([]);

                        if(data.tooltype === 'map-extent'){
                            this.map.map.un('moveend', this.onMoveEnd, this);
                        } 
                    }
                }
            },

            changeDrawingTool: function(map, tooltype){
                this.disableDrawingTools();

                this.modifyTool = new ol.interaction.Modify({
                    features: this.drawingFeatureOverlay.getFeatures(),
                    // the SHIFT key must be pressed to delete vertices, so
                    // that new vertices can be drawn at the same position
                    // of existing vertices
                    deleteCondition: function(event) {
                        return ol.events.condition.shiftKeyOnly(event) &&
                                ol.events.condition.singleClick(event);
                    }
                });
                map.addInteraction(this.modifyTool);                

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

                this.enableDrawingTools();
            },

            enableDrawingTools: function(){
                if(this.drawingtool){
                    this.map.map.addInteraction(this.drawingtool);
                }
            },

            disableDrawingTools: function(){
                if(this.drawingtool){
                    this.map.map.removeInteraction(this.drawingtool);
                }
            },

            removeDrawingTools: function(){
                this.disableDrawingTools();
                delete this.drawingtool;
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
                var params = {
                    filter: ko.toJSON(this.query.filter)
                }; 
                if(this.query.filter.buffer.width() > 0 && this.drawingFeatureOverlay.getFeatures().getLength() > 0){
                    $.ajax({
                        type: "GET",
                        url: arches.urls.buffer,
                        data: {
                            filter: ko.toJSON(this.query.filter)
                        },
                        success: function(results){
                            var source = new ol.source.GeoJSON(({object:{type: 'FeatureCollection', features: [{type:'Feature', geometry: JSON.parse(results)}]}}));
                            var feature = source.getFeatures()[0];
                            
                            feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
                            self.bufferFeatureOverlay.getFeatures().clear();  
                            self.bufferFeatureOverlay.addFeature(feature);
                            self.zoomToExtent(feature.getGeometry().getExtent());
                        },
                        error: function(){}
                    });                    
                }else{
                    this.bufferFeatureOverlay.getFeatures().clear();  
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

            restoreState: function(filter, expanded){
                this.map.map.once('change:size', function(){
                    if(typeof filter !== 'undefined' && 'geometry' in filter && filter.geometry.coordinates.length > 0){
                        this.query.filter.geometry.type(ko.utils.unwrapObservable(filter.geometry.type));
                        this.query.filter.geometry.coordinates(ko.utils.unwrapObservable(filter.geometry.coordinates));
                        this.query.filter.buffer.width(ko.utils.unwrapObservable(filter.buffer.width));
                        this.query.filter.buffer.unit(ko.utils.unwrapObservable(filter.buffer.unit));

                        var coordinates = this.query.filter.geometry.coordinates();
                        var type = this.query.filter.geometry.type();
                        if(type === 'bbox'){
                            this.map.map.on('moveend', this.onMoveEnd, this); 

                            var extent = ol.proj.transformExtent(coordinates, 'EPSG:4326', 'EPSG:3857');
                            this.zoomToExtent(extent);

                        }else{
                            var feature = new ol.Feature({
                                geometry: new ol.geom[type](coordinates)
                            });

                            feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
                            this.zoomToExtent(feature.getGeometry().getExtent());
                            this.drawingFeatureOverlay.addFeature(feature);
                            this.changeDrawingTool(this.map.map, type);
                            this.disableDrawingTools();

                            feature.on('change', function(evt) {
                                var geometry = evt.target.getGeometry().clone();
                                geometry.transform('EPSG:3857', 'EPSG:4326');
                                this.query.filter.geometry.coordinates(geometry.getCoordinates());
                                //self.applyBuffer();
                            }, this);
                        }
                    }

                }, this);

                if(typeof expanded === 'undefined'){
                    expanded = false;
                }
                this.expanded(expanded);

            },

            clear: function(){
                this.query.filter.geometry.type('');
                this.query.filter.geometry.coordinates([]);
                this.disableDrawingTools();
                this.clearDrawingFeatures();
            }

        });
});