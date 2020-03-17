define([
    'knockout',
    'knockout-mapping',
    'viewmodels/card-component',
    'views/components/iiif-annotation'
], function(ko, koMapping, CardComponentViewModel, IIIFAnnotationViewmodel) {
    return ko.components.register('iiif-card', {
        viewModel: function(params) {
            var self = this;

            params.configKeys = ['defaultManifest'];

            CardComponentViewModel.apply(this, [params]);

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
        },
        template: {
            require: 'text!templates/views/components/cards/iiif-card.htm'
        }
    });
});
