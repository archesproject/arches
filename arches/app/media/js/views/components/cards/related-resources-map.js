define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'mapbox-gl',
    'mapbox-gl-draw',
    'geojson-extent',
    'geojsonhint',
    'viewmodels/card-component',
    'views/components/map',
    'views/components/cards/select-feature-layers',
    'text!templates/views/components/cards/related-resources-map-popup.htm',
    'bindings/chosen'
], function(arches, $, _, ko, koMapping, uuid, mapboxgl, MapboxDraw, geojsonExtent, geojsonhint, CardComponentViewModel, MapComponentViewModel, selectFeatureLayersFactory, popupTemplate) {
    var viewModel = function(params) {
        var self = this;
        this.widgets = [];
        var padding = 40;

        params.configKeys = ['selectSource', 'selectSourceLayer'];

        CardComponentViewModel.apply(this, [params]);

        if (self.form && self.tile) self.card.widgets().forEach(function(widget) {
            var id = widget.node_id();
            var type = ko.unwrap(self.form.nodeLookup[id].datatype);
            if (type === 'resource-instance' || type === 'resource-instance-list') {
                self.widgets.push(widget);
            }
        });

        var selectSource = this.selectSource();
        var selectSourceLayer = this.selectSourceLayer();
        var selectedResourceIds = ko.computed(function() {
            var ids = [];
            self.widgets.forEach(function(widget) {
                var id = widget.node_id();
                var value = koMapping.toJS(self.tile.data[id]);
                if (value) {
                    if (Array.isArray(value)) {
                        ids = ids.concat(value);
                    } else {
                        ids.push(value);
                    }
                }
            });
            return ids;
        });
        var selectFeatureLayers = selectFeatureLayersFactory('', selectSource, selectSourceLayer, selectedResourceIds(), true);

        var sources = [];
        for (var sourceName in arches.mapSources) {
            if (arches.mapSources.hasOwnProperty(sourceName)) {
                sources.push(sourceName);
            }
        }
        var updateSelectLayers = function() {
            var source = self.selectSource();
            var sourceLayer = self.selectSourceLayer();
            selectFeatureLayers = sources.indexOf(source) > 0 ?
                selectFeatureLayersFactory('', source, sourceLayer, selectedResourceIds(), true) :
                [];
            self.additionalLayers(
                extendedLayers.concat(
                    selectFeatureLayers
                )
            );
        };
        selectedResourceIds.subscribe(updateSelectLayers);
        this.selectSource.subscribe(updateSelectLayers);
        this.selectSourceLayer.subscribe(updateSelectLayers);

        params.activeTab = 'editor';

        var extendedLayers = [];
        if (params.layers) {
            extendedLayers = params.layers;
        }

        params.layers = ko.observable(
            extendedLayers.concat(selectFeatureLayers)
        );

        MapComponentViewModel.apply(this, [params]);

        this.popupTemplate = popupTemplate;

        this.relateResource = function(popupData, widget) {
            var id = widget.node_id();
            var resourceinstanceid = ko.unwrap(popupData.resourceinstanceid);
            var type = ko.unwrap(self.form.nodeLookup[id].datatype);
            if (type === 'resource-instance') {
                self.tile.data[id](resourceinstanceid);
            } else {
                var value = koMapping.toJS(self.tile.data[id]);
                if (!value) {
                    self.tile.data[id]([resourceinstanceid]);
                } else if (value.indexOf(resourceinstanceid) < 0) {
                    value.push(resourceinstanceid);
                    self.tile.data[id](value);
                }
            }
        };
    };
    ko.components.register('related-resources-map-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/related-resources-map.htm'
        }
    });
    return viewModel;
});
