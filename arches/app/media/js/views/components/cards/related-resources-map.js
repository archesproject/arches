define([
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'geojson-extent',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'viewmodels/map-filter',
    'views/components/cards/select-related-feature-layers',
    'text!templates/views/components/cards/related-resources-map-popup.htm'
], function($, arches, ko, koMapping, geojsonExtent, CardComponentViewModel, MapEditorViewModel, MapFilterViewModel, selectFeatureLayersFactory, popupTemplate) {
    var viewModel = function(params) {
        var self = this;
        this.widgets = [];
        params.configKeys = [
            'selectRelatedSource',
            'selectRelatedSourceLayer',
            'selectLayerConfig',
            'defaultcolor',
            'selectioncolor',
            'hovercolor',
            'colorpalette',
            'fillopacity',
            'overviewzoom',
            'minzoom',
            'pointradius',
            'linewidth',
            'strokecolor',
            'strokelinewidth',
            'strokepointradius',
            'strokepointopacity'
        ];
        CardComponentViewModel.apply(this, [params]);
        var selectLayerConfig = {};
        selectLayerConfig.defaultcolor = this.defaultcolor()
        selectLayerConfig.selectioncolor = this.selectioncolor()
        selectLayerConfig.hovercolor = this.hovercolor()
        selectLayerConfig.colorpalette = typeof this.colorpalette() === 'string' ? this.colorpalette().split(",") : this.colorpalette();
        selectLayerConfig.fillopacity = Number(this.fillopacity());
        selectLayerConfig.overviewzoom = Number(this.overviewzoom());
        selectLayerConfig.minzoom = Number(this.minzoom());
        selectLayerConfig.pointradius = Number(this.pointradius());
        selectLayerConfig.linewidth = Number(this.linewidth());
        selectLayerConfig.strokecolor = this.strokecolor();
        selectLayerConfig.strokelinewidth = Number(this.strokelinewidth());
        selectLayerConfig.strokepointradius = Number(this.strokepointradius());
        selectLayerConfig.strokepointopacity = Number(this.strokepointopacity());
        if (self.form && self.tile) self.card.widgets().forEach(function(widget) {
            var id = widget.node_id();
            var type = ko.unwrap(self.form.nodeLookup[id].datatype);
            if (type === 'resource-instance' || type === 'resource-instance-list' || type === 'geojson-feature-collection') {
                self.widgets.push(widget);
            }
        });
        var getNodeIds = function(){
            var nodeids = [];
            if (self.selectRelatedSource()) {
                var sourceUrl = new window.URL(arches.mapSources[self.selectRelatedSource()].data, window.location.origin);
                var nodes = sourceUrl.searchParams.get('nodeids');
                var node = sourceUrl.searchParams.get('nodeid');
                var nodeids = [];
                if (node) {
                    nodeids.push(node);
                }
                if (nodes) {
                    nodeids = nodeids.concat(nodes.split(','));
                }
            }
            return nodeids;
        };
        this.hoverId = ko.observable();
        this.nodeids = getNodeIds();
        this.nodeDetails = ko.observableArray();
        this.nodeids.forEach(function(nodeid) {
            fetch(arches.urls.api_nodes(nodeid))
              .then(response => response.json())
              .then(data => {
                self.nodeDetails.push(data[0]);
              })
              .catch((error) => {
                console.error('Error:', error);
              });
        })
        var parsedNodeIds = JSON.parse(JSON.stringify(this.nodeids));
        var firstNode = parsedNodeIds.length > 0 ? [parsedNodeIds[0]] : [];
        this.filterNodeIds = ko.observableArray(firstNode);
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
        var selectFeatureLayers = selectFeatureLayersFactory(selectRelatedSource, selectRelatedSourceLayer, selectedResourceIds(), true, null, this.nodeids, this.filterNodeIds(), self.hoverId(), selectLayerConfig);
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
                selectFeatureLayersFactory(source, sourceLayer, selectedResourceIds(), true, null, self.nodeids, self.filterNodeIds(), self.hoverId(), selectLayerConfig) :
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
        this.filterNodeIds.subscribe(updateResourceSelectLayers);
        this.hoverId.subscribe(updateResourceSelectLayers);

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

        this.unrelateResource = function(resourceData, widget) {
            var id = widget.node_id();
            var resourceinstanceid = ko.unwrap(resourceData.resourceinstanceid);
            var related = resourceData.mapCard.tile.data[id]()
            for( var i = 0; i < related.length; i++){ 
                if ( ko.unwrap(related[i].resourceId) === resourceinstanceid) { 
                    related.splice(i, 1); 
                }
            }
            resourceData.mapCard.tile.data[id](related);
        };

        this.isSelectable = function(feature) {
            var selectLayerIds = selectFeatureLayers.map(function(layer) {
                return layer.id;
            });
            return selectLayerIds.indexOf(feature.layer.id) >= 0;
        };

        this.mapFilter = new MapFilterViewModel({
            map: this.map,
            searchContext: self.showRelatedQuery
        });

        this.intersectionSummary = ko.observable({});
        this.updateHoverId = function(val){
            self.hoverId() === val.resourceinstanceid ? self.hoverId(null) : self.hoverId(val.resourceinstanceid);
        };
        this.targetGraphs = ko.observableArray();
        this.mapFilter.filter.feature_collection.subscribe(function(val){
            if (self.widget && self.widget.node.config.graphs().length && val.features && val.features.length > 0) {
                self.targetGraphs.removeAll();
                var graphs = self.widget.node.config.graphs().map(function(v){if (v.graphid){return v.graphid;}});
                self.targetGraphs(graphs);
                graphs.forEach(function(val){
                    if (!self.intersectionSummary()[val]) {
                        var resource = arches.resources.find(function(resource){return resource.graphid === val;});
                        self.intersectionSummary()[val] = resource;
                        self.intersectionSummary()[val].results = ko.observableArray([]);
                    }
                }, this);
                var payload = {
                    "map-filter": JSON.stringify(val),
                    "precision": 6,
                    "pages": 5,
                    "resource-type-filter": JSON.stringify(graphs.map(function(graph) {
                        return {
                            "graphid": graph,
                            "inverted":false
                        };
                    }))};
                $.ajax({
                    url: arches.urls.search_results,
                    data: payload,
                    method: 'GET'
                }).done(function(data){
                    graphs.forEach(function(graph){
                        self.intersectionSummary()[graph].results.removeAll();
                    });
                    self.relatedResourceWidgets.forEach(function(widget) {
                        if (ko.unwrap(self.tile.data[widget.node.nodeid])) {
                            self.tile.data[widget.node.nodeid]([]);
                        }
                    });
                    data.results.hits.hits.forEach(function(hit) {
                        var resourceInstance = hit._source;
                        if (graphs.indexOf(resourceInstance.graph_id) > -1) {
                            self.relateResource(
                                {resourceinstanceid: resourceInstance.resourceinstanceid, graphid: resourceInstance.graph_id},
                                self.widget);
                        }
                        self.intersectionSummary()[resourceInstance.graph_id].results.push(resourceInstance);
                    });
                    self.intersectionSummary.valueHasMutated();
                    var buffer = data['map-filter'].search_buffer;
                    self.map().getSource('geojson-search-buffer-data').setData(buffer);
                });
            }
        });

        this.appendBufferToTileFeatures = function(val){
            var bufferFeature = {geometry: self.map().getSource('geojson-search-buffer-data').serialize().data};
            bufferFeature.type = 'Feature';
            bufferFeature.properties = {};
            var bufferFeatureId = self.draw.add(bufferFeature)[0];
            self.draw.setFeatureProperty(bufferFeatureId, 'nodeId', val);
            self.updateTiles();
        };

        this.drawAvailable.subscribe(function(val){
            var bufferSrcId = 'geojson-search-buffer-data';
            self.widget = self.widgets.find(function(widget){
                return widget.datatype.datatype === 'resource-instance' || widget.datatype.datatype === 'resource-instance-list';
            });
            if (val) {
                self.mapFilter.draw = self.draw;
                self.mapFilter.setupDraw();
                self.map().addSource(bufferSrcId, self.mapFilter.sources[bufferSrcId]);
                self.mapFilter.layers().forEach(function(layer){
                    self.map().addLayer(layer);
                    extendedLayers.push(layer);
                });
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
