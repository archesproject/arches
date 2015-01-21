define(['jquery', 
    'jquery-ui',
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'views/map',
    'openlayers', 
    'knockout',
    'map/resource-layer-model'], 
    function($, jqui, _, Backbone, bootstrap, arches, MapView, ol, ko, ResourceLayerModel) {
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


                this.vectorLayer = new ResourceLayerModel().layer();
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

                this.zoomToExtent(this.vectorLayer.getLayers().item(0).getSource().getExtent())
                
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

                var hoverFeatureInfo = function(pixel) {
                    var info = $('#info');
                    var mapheight = $(self.map.map.getViewport()).height();
                    var mapwidth = $(self.map.map.getViewport()).width();
                    var feature = self.map.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                        if (_.contains(feature.getKeys(), 'primaryname')){
                            return feature.get('primaryname');
                        }
                        if (_.contains(feature.getKeys(), 'features')){
                            // var html = '';
                            // _.find(feature.get('features'), function(feat, index, all){
                            //     if(index < 4){
                            //         html += '<li>' + feat.get("primaryname") + '</li>';
                            //     }else{
                            //         html += '<li>....</li>';
                            //         return false;
                            //     }
                            // });
                            // return html;
                            if(feature.get('features').length === 1){
                                return feature.get('features')[0].get('primaryname');
                            }
                        }
                    });
                    if (feature) {
                        info.find('#tooltip-text').html(feature);
                        if(pixel[0] < mapwidth*.33){
                            info.removeClass('left')
                                .addClass('right');
                        }
                        if(pixel[0] > mapwidth*.66){
                            info.removeClass('right')
                                .addClass('left');
                        }
                        if(info.hasClass('left')){
                            info.css({
                                left: (pixel[0] - info.width() + 20) + 'px',
                                top: (pixel[1] - info.height()/2 - 10) + 'px'
                            });
                        }    
                        if(info.hasClass('right')){
                            info.css({
                                left: (pixel[0] + 50) + 'px',
                                top: (pixel[1] - info.height()/2 - 10) + 'px'
                            });
                        }                 
                        info.fadeIn('fast');
                    } else {
                        info.fadeOut('fast');
                    }
                };

                $(this.map.map.getViewport()).on('mousemove', function(evt) {
                    hoverFeatureInfo(self.map.map.getEventPixel(evt.originalEvent));
                });
            },

            zoomToExtent: function(extent){
                var size = this.map.map.getSize();
                var view = this.map.map.getView()
                view.fitExtent(
                    extent,
                    size
                );
            },

            hexToRgb: function (hex) {
                var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                return result ? {
                    r: parseInt(result[1], 16),
                    g: parseInt(result[2], 16),
                    b: parseInt(result[3], 16)
                } : null;
            },

            highlightFeatures: function(resultsarray){
                var rgb = this.hexToRgb('#C4171D');
                var iconUnicode = '\uf060';

                var style = new ol.style.Style({
                    text: new ol.style.Text({
                        text: iconUnicode,
                        font: 'normal 33px octicons',
                        stroke: new ol.style.Stroke({
                            // color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',1)',
                            color: 'white',
                            width: 3
                        }),
                        textBaseline: 'Bottom',
                        fill: new ol.style.Fill({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                        })
                    })
                });
                var shadowStyle = new ol.style.Style({
                    text: new ol.style.Text({
                        text: iconUnicode,
                        font: 'normal 38px octicons',
                        offsetX: 0,
                        rotation: 0.25,
                        textBaseline: 'Bottom',
                        fill: new ol.style.Fill({
                            color: 'rgba(126,126,126,0.3)',
                        })
                    })
                });
                if(!this.featureOverlay){
                    this.featureOverlay = new ol.FeatureOverlay({
                        map: this.map.map,
                        style: [shadowStyle,style]
                    });                    
                }
                this.featureOverlay.getFeatures().clear();

                _.each(resultsarray.results.hits.hits, function(result){
                    if(result._source.geometries.length > 0){
                        var feature = this.vectorLayer.getLayers().item(0).getSource().getFeatureById(result._id);
                        if(feature){
                            this.featureOverlay.addFeature(feature);
                        }                        
                    }
                }, this);
            },

            selectFeatureById: function(resourceid){
                var rgb = this.hexToRgb('#4CAE4C');
                var iconUnicode = '\uf060';
                
                if(!this.featureHightlightOverlay){
                    this.featureHightlightOverlay = new ol.FeatureOverlay({
                        map: this.map.map,
                        style: new ol.style.Style({
                            text: new ol.style.Text({
                                text: iconUnicode,
                                font: 'normal 33px octicons',
                                stroke: new ol.style.Stroke({
                                    // color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',1)',
                                    color: 'white',
                                    width: 3
                                }),
                                textBaseline: 'Bottom',
                                fill: new ol.style.Fill({
                                    color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                                })
                            })
                        })
                    });                    
                }

                this.unselectAllFeatures();
                var feature = this.vectorLayer.getLayers().item(0).getSource().getFeatureById(resourceid);
                if(feature){
                    this.featureHightlightOverlay.addFeature(feature);
                    return feature;
                } 
            },

            unselectAllFeatures: function(){
                if(this.featureHightlightOverlay) {
                    this.featureHightlightOverlay.getFeatures().clear();
                }
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