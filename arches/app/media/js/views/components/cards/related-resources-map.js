define([
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'geojson-extent',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'viewmodels/map-filter',
    'views/components/cards/select-feature-layers',
    'text!templates/views/components/cards/related-resources-map-popup.htm'
], function($, arches, ko, koMapping, geojsonExtent, CardComponentViewModel, MapEditorViewModel, MapFilterViewModel, selectFeatureLayersFactory, popupTemplate) {
    var viewModel = function(params) {
        var self = this;
        this.widgets = [];
        params.configKeys = ['selectRelatedSource', 'selectRelatedSourceLayer'];
        CardComponentViewModel.apply(this, [params]);

        if (self.form && self.tile) self.card.widgets().forEach(function(widget) {
            var id = widget.node_id();
            var type = ko.unwrap(self.form.nodeLookup[id].datatype);
            if (type === 'resource-instance' || type === 'resource-instance-list' || type === 'geojson-feature-collection') {
                self.widgets.push(widget);
            }
        });

        this.relatedResourceWidgets = this.widgets.filter(function(widget){return widget.datatype.datatype === 'resource-instance' || widget.datatype.datatype === 'resource-instance-list';});
        this.showRelatedQuery = ko.observable(false);
        var resourceBounds = ko.observable();
        var selectRelatedSource = this.selectRelatedSource();
        var selectRelatedSourceLayer = this.selectRelatedSourceLayer();
        var selectedResourceIds = ko.computed(function() {
            var ids = [];
            self.relatedResourceWidgets.forEach(function(widget) {
                var id = widget.node_id();
                var value = ko.unwrap(self.tile.data[id]) ? koMapping.toJS(self.tile.data[id]().map(function(item){return item.resourceId;})) : null;
                if (value) {
                    ids = ids.concat(value);
                }
            });
            return ids;
        });
        var updateResourceBounds = function(ids) {
            if (ids.length > 0) {
                $.getJSON({
                    url: arches.urls.geojson,
                    data: {
                        resourceid: ids.join(',')
                    }
                }, function(geojson) {
                    if (geojson.features.length > 0) resourceBounds(geojsonExtent(geojson));
                });
            }
        };
        updateResourceBounds(selectedResourceIds());
        selectedResourceIds.subscribe(updateResourceBounds);
        var zoomToData = true;
        resourceBounds.subscribe(function(bounds) {
            var map = self.map();
            if (map && map.getStyle() && zoomToData) {
                map.fitBounds(bounds);
            }
            zoomToData = true;
        });
        var selectFeatureLayers = selectFeatureLayersFactory('', selectRelatedSource, selectRelatedSourceLayer, selectedResourceIds(), true);

        var sources = [];
        for (var sourceName in arches.mapSources) {
            if (arches.mapSources.hasOwnProperty(sourceName)) {
                sources.push(sourceName);
            }
        }
        var updateResourceSelectLayers = function() {
            var source = self.selectRelatedSource();
            var sourceLayer = self.selectRelatedSourceLayer();
            selectFeatureLayers = sources.indexOf(source) > 0 ?
                selectFeatureLayersFactory('', source, sourceLayer, selectedResourceIds(), true) :
                [];
            self.additionalLayers(
                extendedLayers.concat(
                    selectFeatureLayers
                )
            );
        };
        selectedResourceIds.subscribe(updateResourceSelectLayers);
        this.selectRelatedSource.subscribe(updateResourceSelectLayers);
        this.selectRelatedSourceLayer.subscribe(updateResourceSelectLayers);

        params.activeTab = 'editor';

        var extendedLayers = [];
        if (params.layers) {
            extendedLayers = params.layers;
        }

        params.layers = ko.observable(
            extendedLayers.concat(selectFeatureLayers)
        );

        params.fitBounds = resourceBounds;
        MapEditorViewModel.apply(this, [params]);
        this.popupTemplate = popupTemplate;

        this.relateResource = function(resourceData, widget) {
            var id = widget.node_id();
            var resourceinstanceid = ko.unwrap(resourceData.resourceinstanceid);
            var type = ko.unwrap(self.form.nodeLookup[id].datatype);
            zoomToData = false;
            var graphconfig = widget.node.config.graphs().find(function(graph){return graph.graphid === ko.unwrap(resourceData.graphid);});
            var val = [{
                ontologyProperty: ko.observable(graphconfig.ontologyProperty || ''),
                inverseOntologyProperty: ko.observable(graphconfig.ontologyProperty || ''),
                resourceId: resourceinstanceid,
                resourceXresourceId: "",
            }];
            if (type === 'resource-instance') {
                self.tile.data[id](val);
            } else {
                var value = koMapping.toJS(self.tile.data[id]);
                if (!value) {
                    self.tile.data[id](val);
                } else if (value.map(function(rr){return rr.resourceId;}).indexOf(resourceinstanceid) < 0) {
                    var values = value.concat(val);
                    self.tile.data[id](values);
                }
            }
        };

        this.isSelectable = function(feature) {
            var selectLayerIds = selectFeatureLayers.map(function(layer) {
                return layer.id;
            });
            return selectLayerIds.indexOf(feature.layer.id) >= 0;
        };

        this.mapFilter = new MapFilterViewModel({
            map: this.map
        });

        this.mapFilter.filter.feature_collection.subscribe(function(val){
            var resourceFilter = {"graphid":"12581535-3a08-11ea-b9b7-027f24e6fd6b","name":"Master Plan Zone","inverted":false}
            var payload = {
                "format": "tilecsv",
                "map-filter": JSON.stringify(val),
                "resource-type-filter": JSON.stringify([resourceFilter]),
                "paging-filter": 1,
                "precision": 6,
                "tiles": true,
                "total": 0
            };
            $.ajax({
                url: arches.urls.search_results,
                data: payload,
                method: 'GET'
            }).done(function(data){
                var widget = self.widgets.find(function(widget){return widget.datatype.datatype === 'resource-instance'});
                data.results.hits.hits.forEach(function(hit) {
                    var resourceInstance = hit._source;
                    self.relateResource(
                        {resourceinstanceid: resourceInstance.resourceinstanceid, graphid: resourceInstance.graph_id},
                        widget);
                });
            });
        });

        this.drawAvailable.subscribe(function(val){
            if (val) {
                self.mapFilter.draw = self.draw;
                self.mapFilter.setupDraw();
            }
        });

    };
    ko.components.register('related-resources-map-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/related-resources-map.htm'
        }
    });
    return viewModel;
});
