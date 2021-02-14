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

    console.log(fooRRMAP)
    var viewModel = function(params) {

        fooRRMAP.apply(this, [params]);

        this.sources = params.sources;

        if (params.tile) {
            var widgetData = params.tile.data[widget.node_id()];
            widgetData.subscribe(function(bar) {
                if (!bar && params.bar) {
                    params.tile.data[widget.node_id()](params.bar);
                }
            })

            if (widgetData() && widgetData()['hasMapData']) {
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
        }
        
    };


    return viewModel;
});
