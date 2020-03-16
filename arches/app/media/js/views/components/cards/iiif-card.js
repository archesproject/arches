define([
    'knockout',
    'viewmodels/card-component',
    'views/components/iiif-annotation'
], function(ko, CardComponentViewModel, IIIFAnnotationViewmodel) {
    return ko.components.register('iiif-card', {
        viewModel: function(params) {
            var self = this;
            
            params.configKeys = ['defaultManifest'];
            
            CardComponentViewModel.apply(this, [params]);
            
            if (!params.manifest)
                params.manifest = this.card.manifest || this.defaultManifest();
            params.canvas = params.canvas || this.card.canvas;
            
            if (this.form && this.tile) {
                params.widgets = this.card.widgets().filter(function(widget) {
                    var id = widget.node_id();
                    var type = ko.unwrap(self.form.nodeLookup[id].datatype);
                    return type === 'annotation';
                });
            }
            
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
