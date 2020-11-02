define([
    'arches',
    'knockout',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'bindings/chosen',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript'
], function(arches, ko, CardComponentViewModel, MapEditorViewModel) {
    var viewModel = function(params) {
        var self = this;

        params.configKeys = [
            'basemap',
            'overlayConfigs',
            'selectSource',
            'selectSourceLayer',
            'selectText',
            'zoom',
            'centerX',
            'centerY'
        ];

        CardComponentViewModel.apply(this, [params]);

        if (self.form && self.tile) {
            params.widgets = self.card.widgets().filter(function(widget) {
                var id = widget.node_id();
                var type = ko.unwrap(self.form.nodeLookup[id].datatype);
                return type === 'geojson-feature-collection';
            });

            for (var widget of params.widgets) {
                widget.config.centerX(self.centerX());
                widget.config.centerY(self.centerY());
                widget.config.zoom(self.zoom());
                widget.config.overlayConfigs(self.overlayConfigs())
                widget.config.basemap(self.basemap());
            }
        }

        if (this.card.overlaysObservable) {
            params.overlaysObservable = this.card.overlaysObservable;
            params.activeBasemap = this.card.activeBasemap;
        }

        if (this.centerX() == 0 && this.centerY() == 0 && this.zoom() == 0) {
            this.centerX(arches.mapDefaultX);
            this.centerY(arches.mapDefaultY);
            this.zoom(arches.mapDefaultZoom);
        }

        // subscriptions need to stay explicit! DRY-ing will break
        this.centerX.subscribe(function(x) {
            if (params.widgets) {
                for (var widget of params.widgets) {
                    widget.config.centerX(x)
                }
            }
        });
        this.centerY.subscribe(function(y) {
            if (params.widgets) {
                for (var widget of params.widgets) {
                    widget.config.centerY(y)
                }
            }
        });
        this.zoom.subscribe(function(zoom) {
            console.log(self, this, zoom, params)
            self.foo(zoom)
            
            if (params.widgets) {
                for (var widget of params.widgets) {
                    widget.config.zoom(zoom)
                }
            }
        });
        this.overlayConfigs.subscribe(function(overlayConfigs) {
            if (params.widgets) {
                for (var widget of params.widgets) {
                    widget.config.overlayConfigs(overlayConfigs)
                }
            }
        });
        this.basemap.subscribe(function(basemap) {
            if (params.widgets) {
                for (var widget of params.widgets) {
                    widget.config.basemap(basemap)
                }
            }
        });

        this.foo = ko.observable(this.zoom());
        params.foo = this.foo;

        params.defaultConfig = self.card.model.get('defaultConfig');

        params.overlayConfigs = this.overlayConfigs;
        params.basemap = this.basemap;
        params.zoom = this.zoom;
        params.x = this.centerX;
        params.y = this.centerY;
        params.usePosition = true;

        MapEditorViewModel.apply(this, [params]);

        this.expandSidePanel = ko.computed(function(){
            if (self.tile) {
                return self.tile.hasprovisionaledits() && self.reviewer === true;
            } else {
                return false;
            }
        });

        this.card.allowProvisionalEditRerender(false);

        if (!this.card.overlaysObservable) {
            this.card.overlaysObservable = this.overlays;
            this.card.activeBasemap = this.activeBasemap;
        }
    };
    ko.components.register('map-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
    return viewModel;
});
