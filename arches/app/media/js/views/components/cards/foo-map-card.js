define([
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'geojson-extent',
    'uuid',
    'views/components/cards/related-resources-map',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'viewmodels/map-filter',
    'views/components/cards/select-related-feature-layers',
    'text!templates/views/components/cards/related-resources-map-popup.htm'
], function($, arches, ko, koMapping, geojsonExtent, uuid, fooRRMAP, CardComponentViewModel, MapEditorViewModel, MapFilterViewModel, selectFeatureLayersFactory, popupTemplate) {


    var foo = function(params) {
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

        /* 
            set/get logic to ensure all data values are equal between parent and children
        */

       this.basemap = ko.observable();
       this.overlayConfigs = ko.observable();
       this.centerX = ko.observable();
       this.centerY = ko.observable();

       for (var widget of self.widgets) {
            if (widget.config.basemap) {
               self.basemap(widget.config.basemap());
            }
            if (widget.config.overlayConfigs) {
                self.overlayConfigs(widget.config.overlayConfigs());
            }
            if (widget.config.centerX) {
                self.centerX(widget.config.centerX());
            }
            if (widget.config.centerY) {
                self.centerY(widget.config.centerY());
            }
        }

        this.basemap.subscribe(function(map) {
            for (var widget of self.widgets) {
                if (widget.config.basemap) {
                    widget.config.basemap(map)
                }
            }
        });
        this.overlayConfigs.subscribe(function(configs) {
            for (var widget of self.widgets) {
                if (widget.config.overlayConfigs) {
                    widget.config.overlayConfigs(configs)
                }
            }
        });
        this.centerX.subscribe(function(x) {
            for (var widget of self.widgets) {
                if (widget.config.centerX) {
                    widget.config.centerX(x)
                }
            }
        });
        this.centerY.subscribe(function(y) {
            for (var widget of self.widgets) {
                if (widget.config.centerY) {
                    widget.config.centerY(y)
                }
            }
        });
        
        this.zoom = ko.observable(this.overviewzoom());
        this.zoom.subscribe(function(zoom) {
            self.config.overviewzoom(zoom);

            for (var widget of self.widgets) {
                if (widget.config.zoom) {
                    widget.config.zoom(zoom)
                }
            }
        });

        /* end local set/get */ 
        
        params.basemap = this.basemap;
        params.overlayConfigs = this.overlayConfigs;
        params.x = this.centerX;
        params.y = this.centerY;
        params.zoom = this.zoom;
        
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
        this.relatedResourceDetails = {};
        this.relatedResourceWidgets = this.widgets.filter(function(widget){return widget.datatype.datatype === 'resource-instance' || widget.datatype.datatype === 'resource-instance-list';});
        this.relatedResources = ko.pureComputed(function() {
            var tileResourceIds = [];
            self.relatedResourceWidgets.forEach(function(widget) {
                var nodeid = ko.unwrap(widget.node_id);
                var related = self.tile.data[nodeid]();
                if (related) {
                    self.tile.data[nodeid]().forEach(function(rr) {
                        var resourceinstanceid = ko.unwrap(rr.resourceId);
                        if (resourceinstanceid) {
                            tileResourceIds.push(resourceinstanceid);
                            if (!self.relatedResourceDetails[resourceinstanceid]) {
                                window.fetch(arches.urls.search_results + "?id=" + resourceinstanceid)
                                    .then(function(response) {
                                        if (response.ok) {
                                            return response.json();
                                        }
                                    })
                                    .then(function(json) {
                                        var details = json.results.hits.hits[0]._source
                                        self.relatedResourceDetails[resourceinstanceid] = {graphid: details.graph_id, resourceinstanceid: resourceinstanceid, displayname: details.displayname};
                                        self.tile.data[nodeid].valueHasMutated();
                                    });
                            }
                        }
                    });
                }
            });
            return tileResourceIds
                .map(function(resourceid){return self.relatedResourceDetails[resourceid]})
                .filter(function(val){return val !== undefined});
        });

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
                selectFeatureLayers.concat(
                    extendedLayers
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
            self.relatedResourceDetails[ko.unwrap(resourceData.resourceinstanceid)] = {
                graphid: ko.unwrap(resourceData.graphid),
                displayname: ko.unwrap(resourceData.displayname),
                resourceinstanceid: ko.unwrap(resourceData.resourceinstanceid)
            }
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

        this.updateHoverId = function(val){
            self.hoverId() === val.resourceinstanceid ? self.hoverId(null) : self.hoverId(val.resourceinstanceid);
        };
        this.mapFilter.filter.feature_collection.subscribe(function(val){
            if (self.widget && self.widget.node.config.graphs().length && val.features && val.features.length > 0) {
                var graphs = self.widget.node.config.graphs().map(function(v){if (v.graphid){return v.graphid;}});
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
                    self.relatedResourceWidgets.forEach(function(widget) {
                        if (ko.unwrap(self.tile.data[widget.node.nodeid])) {
                            self.tile.data[widget.node.nodeid]([]);
                        }
                    });
                    data.results.hits.hits.forEach(function(hit) {
                        var resourceInstance = hit._source;
                        if (graphs.indexOf(resourceInstance.graph_id) > -1) {
                            self.relateResource(
                                {resourceinstanceid: resourceInstance.resourceinstanceid, graphid: resourceInstance.graph_id, displayname: resourceInstance.displayname},
                                self.widget);
                        }
                    });
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
                self.map().on('mousemove', (e) => {
                    var features = self.map().queryRenderedFeatures(e.point);
                    var feature;
                    if (features.length && features[0].properties.resourceinstanceid) {
                        feature = features[0].properties.resourceinstanceid;
                        if (self.relatedResources().filter(function(val){return val.resourceinstanceid === feature}).length) {
                            self.hoverId(feature);
                        }
                    } else {
                        self.hoverId(null);
                    }
                });
            }
        });

    };


    var viewModel = function(params) {
        var self = this;
        ko.utils.extend(self, new foo(params))


        
        // if (!params.foobar) {
        //     params.foobar = ko.observable();
        // }
        // this.foobar = params.foobar;



        if (params.tile && params.card) {

            params.card.widgets().forEach(function(widget) {
                self.widgets.push(widget);


                var widgetData = params.tile.data[widget.node_id()];
                console.log("FJDISOFJIODSFDS", self, params, widgetData())


                if (!widgetData() && widget.boofar) {
                    params.tile.data[widget.node_id()](widget.boofar)
                }

                widgetData.subscribe(function(bar) {
                    console.log("dhdh", self,  params, widgetData(), bar, widget)
                    // if (bar) {
                    //     console.log(bar, self, params)
                    //     bar.data.forEach(function(baz) {
                    //         Object.values(baz).forEach(function(qux) {

                    //             if (!params['parsedFileLookup']) {
                    //                 params['parsedFileLookup'] = {};
                    //             } 

                    //             params['parsedFileLookup'][baz.meta.id] = widgetData().data.find(function(qux) {
                    //                 return qux['meta']['id'] === baz.meta.id;
                    //             });
                            
                    //         });
                    //     });


                    // }


                    // if (!params.foobar) {
                    //     params.foobar = ko.observable()
                    // }

                    if (bar) {
                        widget.boofar = bar;
                        // params.foobar(bar)

                        // if (params['sources']) {
                        //     params['sources']['geojson-editor-data']['data']['features'].push(bar);
                        // }


                        // Object.values(bar).forEach(function(baz) {
                        //     if (baz instanceof Object && baz['features']) {
                        //         baz.features.forEach(function(feature) {
                        //             params['sources']['geojson-editor-data']['data']['features'].push(feature);
                        //         });
                        //     }
                        // });

                        
                    }

                    // if (!params.tile.data[widget.node_id()] && params.foobar()) {
                    //     params.tile.data[widget.node_id()] = params.foobar();
                    // }




                    // if (!bar && params.bar) {
                        // params.tile.data[widget.node_id()](bar);
                        // params.value(bar)
                    // }
                })
    
                if (widgetData()) {
                    self.widgets.push(widget);
    
    
                    // UNDO THIS
                    console.log('OY THERE', widget, widgetData())
                    widgetData().data.forEach(function(foo) {
                        Object.values(foo).forEach(function(bar) {
                            if (bar instanceof Object && bar['geometry'] && bar['geometry']['coordinates']) {
                                var qux = {
                                    id: foo.meta.id,
                                    nodeId: foo.meta.nodeId,
                                    ...bar
                                };
    
    
                                if (!params['bar']) {
                                    params['bar'] = {};
                                }
    
                                params['bar'][foo.meta.id] = widgetData().data.find(function(qux) {
                                    return qux['meta']['id'] === foo.meta.id;
                                });
    
                                if (!params['foo']) {
                                    params['foo'] = [qux];
                                }
                                else {
                                    params['foo'].push(qux);
                                }
                                if (params['sources']) {
    
                                    params['sources']['geojson-editor-data']['data']['features'].push(bar);
                                }
                            }
                        });
                    });
                }
            })
        }
        

        self.map.subscribe(function(fooMap) {
            // console.log("REALLY?", fooMap)

            fooMap.on('click', function(e) {
                // console.log("EDITOR CLICK", e, self, params)
                var hoverFeature = _.find(
                    fooMap.queryRenderedFeatures(e.point),
                    function(feature) { return feature.properties.id; }
                );

                if (hoverFeature) {
                    console.log(params['bar'][hoverFeature['properties']['id']])
                    self.popup = new mapboxgl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(`<div>${Object.values(params['bar'][hoverFeature['properties']['id']])}</div>`)
                        .addTo(fooMap);
                }
            })

            // params['foo'].forEach(function(bar) {
            //     // bar['id'] = uuid.generate();
            //     console.log(bar)
            //     self.draw.add(bar)
            //     // params['sources']['geojson-editor-data']['data']['features'].push(bar)
            // });

        })
        // console.log("SSSSS", params, self, self.draw)

        // var id = ko.unwrap(params.foo[0].nodeId);

        // self.featureLookup[id] = {
        //     features: params.foo,
        //     selectedTool: ko.observable(),
        //     dropErrors: ko.observableArray()
        // };
        // self.featureLookup[id].selectedTool.subscribe(function(tool) {
        //     if (self.draw) {
        //         if (tool === '') {
        //             self.draw.trash();
        //             self.draw.changeMode('simple_select');
        //         } else if (tool) {
        //             _.each(self.featureLookup, function(value, key) {
        //                 if (key !== id) {
        //                     value.selectedTool(null);
        //                 }
        //             });
        //             self.newNodeId = id;
        //         }
        //         self.setDrawTool(tool);
        //     }
        // });


        // params.usePosition = false;
        // params.bounds = geojsonExtent({
        //     type: 'FeatureCollection',
        //     features: params['foo']
        // });
        // console.log("HERE YOU", self, params, params.bounds)

    }



    return viewModel;
});
