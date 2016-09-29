define([
  'knockout',
  'underscore',
  'viewmodels/widget',
  'arches',
  'map/mapbox-style',
  'bindings/fadeVisible',
  'bindings/mapbox-gl',
  'bindings/chosen'
], function (ko, _, WidgetViewModel, arches, mapStyle) {
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

            var self = this;
            params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes'];
            WidgetViewModel.apply(this, [params]);
            this.selectedBasemap = this.basemap;

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

            this.geocoderOptions = ko.observableArray([{'id':'MapzenGeocoder','name':'Mapzen'},{'id':'BingGeocoder','name':'Bing'}]);

            this.onGeocodeSelection = function(val, e) {
              this.geocoder(e.currentTarget.value)
              console.log(val, e);
            }

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
