define([
    'knockout',
    'viewmodels/widget',
    'views/components/iiif-annotation'
], function(ko, WidgetViewModel, IIIFAnnotationViewmodel) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
            var self = this;
            
            params.configKeys = ['defaultManifest'];
            WidgetViewModel.apply(this, [params]);
            
            if (params.widget) params.widgets = [params.widget];
            if (!params.manifest) params.manifest = this.defaultManifest();
            
            IIIFAnnotationViewmodel.apply(this, [params]);
            
            this.manifest.subscribe(function(manifest) {
                if (manifest !== self.defaultManifest())
                    self.defaultManifest(manifest);
            });
            
            this.defaultManifest.subscribe(function(manifest) {
                if (manifest !== self.manifest())
                    self.manifest(manifest);
            });
        },
        template: { require: 'text!templates/views/components/widgets/iiif.htm' }
    });
});
