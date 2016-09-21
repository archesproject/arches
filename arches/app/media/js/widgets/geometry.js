define([
  'knockout',
  'underscore',
  'viewmodels/widget',
  'arches',
  'map/mapbox-style',
  'geoms',
  'bindings/map-controls',
  'bindings/mapbox-gl'
], function (ko, _, WidgetViewModel, arches, mapStyle, geoms) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a geometry-widget component for use in forms
    * @function external:"ko.components".geometry-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the select input
    * @param {string} params.config.trueValue - label alongside the true boolean button
    * @param {string} params.config.falseValue - label alongside the false boolean button
    */
    return ko.components.register('geometry-widget', {
        viewModel: function(params) {
              var drawConstants = {
                            classes: {
                              CONTROL_BASE: 'mapboxgl-ctrl',
                              CONTROL_PREFIX: 'mapboxgl-ctrl-',
                              CONTROL_BUTTON: 'mapbox-gl-draw_ctrl-draw-btn',
                              CONTROL_BUTTON_LINE: 'mapbox-gl-draw_line',
                              CONTROL_BUTTON_POLYGON: 'mapbox-gl-draw_polygon',
                              CONTROL_BUTTON_POINT: 'mapbox-gl-draw_point',
                              CONTROL_BUTTON_TRASH: 'mapbox-gl-draw_trash',
                              CONTROL_GROUP: 'mapboxgl-ctrl-group',
                              ATTRIBUTION: 'mapboxgl-ctrl-attrib',
                              ACTIVE_BUTTON: 'active',
                              BOX_SELECT: 'mapbox-gl-draw_boxselect'
                            },
                            sources: {
                              HOT: 'mapbox-gl-draw-hot',
                              COLD: 'mapbox-gl-draw-cold'
                            },
                            cursors: {
                              ADD: 'add',
                              MOVE: 'move',
                              DRAG: 'drag',
                              POINTER: 'pointer',
                              NONE: 'none'
                            },
                            types: {
                              POLYGON: 'polygon',
                              LINE: 'line_string',
                              POINT: 'point'
                            },
                            modes: {
                              DRAW_LINE_STRING: 'draw_line_string',
                              DRAW_POLYGON: 'draw_polygon',
                              DRAW_POINT: 'draw_point',
                              SIMPLE_SELECT: 'simple_select',
                              DIRECT_SELECT: 'direct_select',
                              STATIC: 'static'
                            }
                          };

            var self = this;
            params.configKeys = ['zoom', 'centerX', 'centerY', 'defaultgeocoder', 'basemap', 'baseMaps', 'geometryTypes'];
            WidgetViewModel.apply(this, [params]);
            this.selectedBasemap = this.basemap;
            var layers = [];

            arches.basemapLayers.forEach(function (layer) {
              if (layer.name === self.selectedBasemap()) {
                  layers.push(layer.layer);
                  }
            });

            this.mapToolsExpanded = ko.observable(false);
            this.geocodeShimAdded = ko.observable(false);
            this.mapToolsExpanded.subscribe(function (expanded) {
               self.geocodeShimAdded(expanded);
            });

            this.mapControlPanels = {
              basemaps: ko.observable(false),
              overlays: ko.observable(true),
              maptools: ko.observable(true),
              legend: ko.observable(true)
            };

            this.toggleMapTools = function(data, event){
                data.mapToolsExpanded(!data.mapToolsExpanded());
            }

            this.toggleMapControlPanels = function(data, event){
                var panel = data;
                _.each(self.mapControlPanels, function(panelValue, panelName) {
                    panelName === panel ? panelValue(false) : panelValue(true);
                  }
                  );
            }

            mapStyle.layers = layers;

            this.mapOptions = {
                style: mapStyle
            };

            this.selectBasemap = function(val){
              self.basemap(val.name)
              self.setBasemap(val);
            }

        },
        template: { require: 'text!widget-templates/geometry' }
    });
});
