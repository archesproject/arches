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

        params.zoom = this.zoom;
        params.x = this.centerX;
        params.y = this.centerY;
        params.usePosition = true;

        params.x.subscribe(function(foo) {
            if (params.widgets) {
                params.widgets[0].config.centerX(foo)
            }
        })
        params.y.subscribe(function(foo) {
            if (params.widgets) {
                params.widgets[0].config.centerY(foo)
            }
        })
        params.zoom.subscribe(function(foo) {
            if (params.widgets) {
                params.widgets[0].config.zoom(foo)
            }
        })

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
