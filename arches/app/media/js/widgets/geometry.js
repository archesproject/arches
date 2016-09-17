define([
  'knockout',
  'underscore',
  'openlayers',
  'viewmodels/widget'
], function (ko, _, ol, WidgetViewModel) {
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
            params.configKeys = ['zoom'];
            var self = this;
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
            WidgetViewModel.apply(this, [params]);
            var baselayer = new ol.layer.Tile({
              source: new ol.source.OSM()
            });
            var coords = ol.proj.transform([params.config().centerX, params.config().centerY], 'EPSG:4326','EPSG:3857');
            this.map = new ol.Map({
              layers: [baselayer],
              target: 'map',
              view: new ol.View({
                center: coords,
                zoom: params.config().zoom
              })
            });
        },
        template: { require: 'text!widget-templates/geometry' }
    });
});
