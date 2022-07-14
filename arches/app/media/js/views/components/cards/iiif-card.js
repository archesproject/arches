define([
    'knockout',
    'knockout-mapping',
    'viewmodels/card-component',
    'views/components/iiif-annotation',
    'viewmodels/alert',
    'templates/views/components/cards/iiif-card.htm',
], function(ko, koMapping, CardComponentViewModel, IIIFAnnotationViewmodel, AlertViewModel, iiifCardTemplate) {
    const viewModel = function(params) {
        var self = this;

        params.configKeys = ['defaultManifest'];
         

        CardComponentViewModel.apply(this, [params]);

        var newTile = true;
        if (self.tile) newTile = !self.tile.tileid;

        if (newTile) {
            this.onSaveSuccess = function() {
                self.card.center = self.map().getCenter();
                self.card.zoom = self.map().getZoom();
            };
        }

        this.deleteTile = function() {
            self.loading(true);
            self.tile.deleteTile(function(response) {
                self.loading(false);
                params.pageVm.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        response.responseJSON.title,
                        response.responseJSON.message,
                        null,
                        function() { }
                    )
                );
                if (params.form.onDeleteError) {
                    params.form.onDeleteError(self.tile);
                }
            }, function() {
                self.loading(false);
                if (!self.card.tiles().length) {
                    self.card.manifest = undefined;
                    self.card.canvas = undefined;
                }
                if (params.form.onDeleteSuccess) {
                    params.form.onDeleteSuccess(self.tile);
                }
            });
        };

        if (this.form && this.tile) {
            params.widgets = this.card.widgets().filter(function(widget) {
                var id = widget.node_id();
                var type = ko.unwrap(self.form.nodeLookup[id].datatype);
                return type === 'annotation';
            });
            params.widgets.forEach(function(widget) {
                var id = widget.node_id();
                var featureCollection = koMapping.toJS(self.tile.data[id]);
                if (featureCollection) {
                    featureCollection.features.forEach(function(feature) {
                        if (feature.properties.manifest && !params.manifest)
                            params.manifest = feature.properties.manifest;
                        if (feature.properties.canvas && !params.canvas)
                            params.canvas = feature.properties.canvas;
                    });
                }
            });
        }

        if (!params.manifest)
            params.manifest = this.card.manifest || this.defaultManifest();
        params.canvas = params.canvas || this.card.canvas;
        params.center = this.card.center;
        params.zoom = this.card.zoom;
        params.expandGallery = this.card.expandGallery;
        params.showGallery = this.card.showGallery;

        IIIFAnnotationViewmodel.apply(this, [params]);

        if (this.form && !this.preview) {
            this.card.manifest = this.manifest();
            this.card.canvas = this.canvas();
            this.manifest.subscribe(function(manifest) {
                self.card.manifest = manifest;
            });
            this.canvas.subscribe(function(canvas) {
                self.card.canvas = canvas;
            });
        }

        if (this.preview) {
            this.manifest.subscribe(function(m) {
                if (m !== self.defaultManifest()) self.defaultManifest(m);
            });
            this.defaultManifest.subscribe(function(m) {
                if (m !== self.manifest()) self.manifest(m);
            });
        }

        self.card.center = undefined;
        self.card.zoom = undefined;
        self.expandGallery.subscribe(function(expandGallery) {
            self.card.expandGallery = expandGallery;
        });
        self.showGallery.subscribe(function(showGallery) {
            self.card.showGallery = showGallery;
        });
    };

    ko.components.register('iiif-card', {
        viewModel: viewModel,
        template: iiifCardTemplate,
    });
    return viewModel;
});
