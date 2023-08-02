define([
    'arches',
    'knockout',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'bindings/chosen',
    'bindings/codemirror'
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

        var widgets = [];

        if (self.form && self.tile) {
            widgets = self.card.widgets().filter(function(widget) {
                var id = widget.node_id();
                var type = ko.unwrap(self.form.nodeLookup[id].datatype);
                return type === 'geojson-feature-collection';
            });

            for (var widget of widgets) {
                widget.config.basemap(self.basemap());
                widget.config.overlayConfigs(self.overlayConfigs())
                widget.config.centerX(self.centerX());
                widget.config.centerY(self.centerY());
                widget.config.zoom(self.zoom());
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
        this.basemap.subscribe(function(basemap) {
            if (self.config.basemap() !== basemap) {
                self.config.basemap(basemap);
            }

            for (var widget of widgets) {
                widget.config.basemap(basemap);
            }
        });
        this.overlayConfigs.subscribe(function(overlayConfigs) {
            if (self.config.overlayConfigs() !== overlayConfigs) {
                self.config.overlayConfigs(overlayConfigs);
            }

            for (var widget of widgets) {
                widget.config.overlayConfigs(overlayConfigs);
            }
        });
        this.centerX.subscribe(function(x) {
            if (self.config.centerX() !== x) {
                self.config.centerX(x);
            }

            self.centerX(x); /* forces card-control update */
            
            for (var widget of widgets) {
                widget.config.centerX(x);
            }
        });
        this.centerY.subscribe(function(y) {
            if (self.config.centerY() !== y) {
                self.config.centerY(y);
            }

            self.centerY(y); /* forces card-control update */

            for (var widget of widgets) {
                widget.config.centerY(y);
            }
        });
        this.zoom.subscribe(function(zoom) {
            if (self.config.zoom() !== zoom) {
                self.config.zoom(zoom);
            }
            
            self.zoom(zoom); /* forces card-control update */

            for (var widget of widgets) {
                widget.config.zoom(zoom);
            }
        });

        params.defaultConfig = self.card.model.get('defaultConfig');
        params.overlayConfigs = this.overlayConfigs;
        params.basemap = this.basemap;
        params.x = this.centerX;
        params.y = this.centerY;
        params.zoom = this.zoom;
        params.usePosition = true;
        params.widgets = widgets;

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
