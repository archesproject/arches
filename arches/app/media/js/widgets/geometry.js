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
            params.configKeys = ['trueLabel', 'falseLabel'];
            WidgetViewModel.apply(this, [params]);
            var baselayer = new ol.layer.Tile({
              source: new ol.source.OSM()
            });
            var map = new ol.Map({
              layers: [baselayer],
              target: 'map',
              view: new ol.View({
                center: [-11000000, 4600000],
                zoom: 4
              })
            });
        },
        template: { require: 'text!widget-templates/geometry' }
    });
});
