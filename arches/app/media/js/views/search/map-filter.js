define(['jquery', 
    'jquery-ui',
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'views/map',
    'openlayers', 
    'knockout',
    'map/resource-layer-model',
    'utils'], 
    function($, jqui, _, Backbone, bootstrap, arches, MapView, ol, ko, ResourceLayerModel, utils) {
        var geoJSON = new ol.format.GeoJSON();
        return Backbone.View.extend({

            events: {
                'click .layer-zoom': 'layerZoom'
            },

            initialize: function(options) { 
                var self = this;

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
                        self.togglefilter(evt);
                    }
                    return false;
                });

                //  suppress default bahavior of the bootstrap menu to auto close
                $('#map-tools-btn').on('hide.bs.dropdown', false);            
                $('#map-tools-btn').on('show.bs.dropdown', false);


                this.expanded = ko.observable(false);
                this.expanded.subscribe(function(status){
                    this.toggleFilterSection($('#map-filter'), status);
                }, this);

                this.query = {
                    filter: {
                        geometry:{
                            type: ko.observable(''),
                            coordinates: ko.observable([])
                        },
                        buffer: {
                            width: ko.observable('0'),
                            unit: ko.observable('ft')
                        },
                        inverted: ko.observable(false)
                    },
                    changed: ko.pureComputed(function(){
                        return (ko.toJSON(this.query.filter.geometry.coordinates()) + 
                            ko.toJSON(this.query.filter.buffer.width()) + 
                            ko.toJSON(this.query.filter.inverted()));
                    }, this).extend({ rateLimit: 200 })
                }

                ko.applyBindings(this.query.filter, $('#map-tools-dropdown')[0]); 

                this.query.filter.buffer.width.subscribe(function(){
                    self.applyBuffer();
                });

                this.query.filter.geometry.type.subscribe(function(type){
                    var enabled = type !== '';
                    this.trigger('enabled', enabled, this.query.filter.inverted());
                    return enabled;
                }, this);


                this.vectorLayer = new ResourceLayerModel({}, function(features){
                    self.trigger('vectorlayerloaded', features);
                    if (!self.cancelFitBaseLayer){
                        setTimeout(function() {
                              self.zoomToExtent(self.vectorLayer.getSource().getExtent());
                        }, 500);                        
                    }
                }).layer();
                this.map = new MapView({
                    el: $('#map'),
                    overlays: [this.vectorLayer]
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
                
                ko.applyBindings(this.map, $('#basemaps-panel')[0]);

                var hideAllPanels = function(){
                    $("#basemaps-panel").addClass("hidden");

                    //Update state of remaining buttons
                    $("#inventory-basemaps")
                        .removeClass("arches-map-tools-pressed")
                        .addClass("arches-map-tools")
                        .css("border-bottom-left-radius", "1px");
                };

                //Inventory-basemaps button opens basemap panel
                $("#inventory-basemaps").click(function (){
                    if ($(this).hasClass('arches-map-tools-pressed')) {
                        hideAllPanels();
                    } else {
                        $("#basemaps-panel").removeClass("hidden");

                        //Update state of current button and adjust position
                        $("#inventory-basemaps")
                            .addClass("arches-map-tools-pressed")
                            .removeClass("arches-map-tools")
                            .css("border-bottom-left-radius", "5px");
                    }
                });

                $(".basemap").click(function (){ 
                    var basemap = $(this).attr('id');
                    _.each(self.map.baseLayers, function(baseLayer){ 
                        baseLayer.layer.setVisible(baseLayer.id == basemap);
                    });
                    hideAllPanels();
                });

                //Close Button
                $(".close").click(function (){ 
                    hideAllPanels();
                });

                
                var mouseoverFeatureTooltip = $('#feature_tooltip');
                var currentMousePx = null;
                var archesFeaturesCache = {};

                var showMouseoverFeatureTooltip = function(feature) {
                    var mapheight = self.map.$el.height();
                    var mapwidth = self.map.$el.width();
                    if (currentMousePx) {
                        mouseoverFeatureTooltip.find('#tooltip-text').html(feature.get('primaryname'));
                        if(currentMousePx[0] < mapwidth*0.33){
                            mouseoverFeatureTooltip.removeClass('left')
                                .addClass('right');
                        }
                        if(currentMousePx[0] > mapwidth*0.66){
                            mouseoverFeatureTooltip.removeClass('right')
                                .addClass('left');
                        }
                        if(mouseoverFeatureTooltip.hasClass('left')){
                            mouseoverFeatureTooltip.css({
                                left: (currentMousePx[0] - mouseoverFeatureTooltip.width()+20) + 'px',
                                top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2) + 'px'
                            });
                        }
                        if(mouseoverFeatureTooltip.hasClass('right')){
                            mouseoverFeatureTooltip.css({
                                left: (currentMousePx[0] + 45) + 'px',
                                top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2) + 'px'
                            });
                        }
                        mouseoverFeatureTooltip.show();
                    }
                };

                self.map.on('mousePositionChanged', function (mousePosition, pixels, feature) {
                    var cursorStyle = "";
                    currentMousePx = pixels;

                    if (feature && (feature.get('arches_marker') || feature.get('arches_cluster'))) {
                        cursorStyle = "pointer";
                        if (feature.get('arches_marker') || feature.get('features').length === 1) {
                            if (feature.get('features')) {
                                feature = feature.get('features')[0];
                            }
                            var fullFeature = archesFeaturesCache[feature.getId()];
                            if (fullFeature && fullFeature != 'loading') {
                                showMouseoverFeatureTooltip(fullFeature);
                            } else if (fullFeature != 'loading') {
                                archesFeaturesCache[feature.getId()] = 'loading';
                                $.ajax({
                                    url: arches.urls.map_markers + 'all?entityid=' + feature.getId(),
                                    success: function(response) {
                                        fullFeature = geoJSON.readFeature(response.features[0]);
                                        var geom = fullFeature.getGeometry();
                                        geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

                                        fullFeature.set('select_feature', true);
                                        fullFeature.set('entityid', fullFeature.getId());

                                        archesFeaturesCache[feature.getId()] = fullFeature;
                                        showMouseoverFeatureTooltip(fullFeature);
                                    }
                                });
                            }
                        }
                    } else {
                        mouseoverFeatureTooltip.hide();
                    }
                    self.map.$el.css("cursor", cursorStyle);
                });
            },

            zoomToResource: function(resourceid){
                this.cancelFitBaseLayer = true;
                var feature = this.selectedFeatureLayer.getSource().getFeatureById(resourceid);
                if(feature.getGeometry().getGeometries().length > 1){
                    var extent = feature.getGeometry().getExtent();
                    var minX = extent[0];
                    var minY = extent[1];
                    var maxX = extent[2];
                    var maxY = extent[3];
                    var polygon = new ol.geom.Polygon([[[minX, minY], [maxX, minY], [maxX, maxY], [minX, maxY], [minX, minY]]]);
                    //polygon.transform('EPSG:3857', 'EPSG:4326');
                    this.map.map.getView().fitGeometry(polygon, this.map.map.getSize(), {maxZoom:16}); 
                    //this.zoomToExtent(feature.getGeometry().getExtent());
                }else{
                    this.map.map.getView().fitGeometry(feature.getGeometry().getGeometries()[0], this.map.map.getSize(), {maxZoom:16});                    
                }
            },
            
            zoomToExtent: function(extent){
                var size = this.map.map.getSize();
                var view = this.map.map.getView()
                view.fitExtent(
                    extent,
                    size
                );
            },

            highlightFeatures: function(resultsarray, entityIdArray){
                var source, geometries;
                var self = this;
                var f = new ol.format.GeoJSON({defaultDataProjection: 'EPSG:4326'});

                if(!this.selectedFeatureLayer){
                    var iconUnicode = '\uf060';
                    this.selectedFeatureLayer = new ResourceLayerModel({entitytypeid: null, vectorColor: '#C4171D'}).layer();
                    this.map.map.addLayer(this.selectedFeatureLayer);
                    var styleFactory = function (color, zIndex) {
                        var rgb = utils.hexToRgb(color);
                        return [new ol.style.Style({
                            text: new ol.style.Text({
                                text: iconUnicode,
                                font: 'normal 50px octicons',
                                offsetX: 5,
                                offsetY: ((50/2)*-1)-5,
                                fill: new ol.style.Fill({
                                    color: 'rgba(126,126,126,0.3)',
                                })
                            }),
                            zIndex: zIndex
                        }), new ol.style.Style({
                            text: new ol.style.Text({
                                text: iconUnicode,
                                font: 'normal 50px octicons',
                                offsetY: (50/2)*-1,
                                stroke: new ol.style.Stroke({
                                    color: 'white',
                                    width: 3
                                }),
                                fill: new ol.style.Fill({
                                    color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                                })
                            }),
                            zIndex: zIndex
                        })]
                    }
                    var normalStyle = styleFactory('#C4171D', 1000000);
                    var highlightStyle = styleFactory('#4CAE4C', 9999999);

                    this.currentPageLayer = new ol.layer.Vector({
                        source: new ol.source.GeoJSON(),
                        style: function(feature) {
                            if(feature.get('highlight')) {
                                return highlightStyle;
                            } else {
                                return normalStyle;
                            }
                        }
                    });
                    this.map.map.addLayer(this.currentPageLayer);  
                }
                var previousSelections = this.selectedFeatureLayer.vectorSource.getFeatures().concat(this.currentPageLayer.getSource().getFeatures())
                _.each(previousSelections, function(feature) {
                    self.vectorLayer.vectorSource.addFeature(feature);
                });
                this.selectedFeatureLayer.vectorSource.clear();
                this.currentPageLayer.getSource().clear();

                var features = _.filter(this.vectorLayer.vectorSource.getFeatures(), function(feature){ return _.contains(entityIdArray, feature.getId()) });

                _.each(features, function(feature) {
                    self.vectorLayer.vectorSource.removeFeature(feature);
                    if (!feature.get('arches_marker')) {
                        feature.set('arches_marker', true);
                    }
                    if (_.find(resultsarray.results.hits.hits, function(hit){ return hit['_id'] === feature.getId()})) {
                        self.currentPageLayer.getSource().addFeature(feature);
                    } else {
                        self.selectedFeatureLayer.vectorSource.addFeature(feature);
                    }
                });

                _.each(features, function(feature){
                    
                }, this);
            },

            selectFeatureById: function(resourceid){
                this.unselectAllFeatures();
                var feature = this.currentPageLayer.getSource().getFeatureById(resourceid);
                if(feature){
                    feature.set('highlight', true);
                    return feature;
                } 
            },

            unselectAllFeatures: function(){
                this.currentPageLayer.getSource().forEachFeature(function(feature) {
                    feature.set('highlight', false);
                });
            },

            getMapExtent: function(){
                var extent = ol.proj.transformExtent(this.map.map.getView().calculateExtent(this.map.map.getSize()), 'EPSG:3857', 'EPSG:4326');
                return extent;
            },

            onMoveEnd: function(evt) {
                this.query.filter.geometry.coordinates(this.getMapExtent());
            },

            togglefilter: function(evt){
                var link = $(evt.target).closest('a');
                var data = link.data();
                var item = link.find('i');
 
                if (!(item.hasClass("fa-check"))){
                    this.enableFilter(data.tooltype);
                }else{
                    this.clear();
                }
            },

            enableFilter: function(tooltype){
                if(tooltype){
                    if(tooltype === 'map-extent'){
                        this.removeDrawingTools();
                        this.clearDrawingFeatures();
                        this.query.filter.geometry.type('bbox');
                        this.query.filter.geometry.coordinates(this.getMapExtent());
                        this.map.map.on('moveend', this.onMoveEnd, this);
                    }else{
                        this.clearDrawingFeatures();
                        this.query.filter.geometry.type(tooltype);
                        this.changeDrawingTool(this.map.map, tooltype);
                        this.map.map.un('moveend', this.onMoveEnd, this);     
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
                this.drawingtool.set('type', tooltype);

                this.drawingtool.on('drawstart', function(){
                    if(this.drawingtool.get('type') !== 'Point'){
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
                        this.query.filter.inverted(ko.utils.unwrapObservable(filter.inverted));                        
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
                this.removeDrawingTools();
                this.clearDrawingFeatures();
                this.query.filter.inverted(false);
                this.query.filter.geometry.type('');
                this.query.filter.geometry.coordinates([]);
                this.map.map.un('moveend', this.onMoveEnd, this);
            }

        });
});