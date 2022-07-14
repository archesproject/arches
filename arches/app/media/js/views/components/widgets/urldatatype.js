define([
    'knockout', 
    'viewmodels/widget',
    'templates/views/components/widgets/urldatatype.htm',
], function(ko, WidgetViewModel, urlDatatypeWidgetTemplate) {
    var name = 'urldatatype';
    const viewModel = function(params) {
        params.configKeys = ['url_placeholder','url_label_placeholder','link_color'];
        params.valueProperties = ['url', 'url_label'];

         
        WidgetViewModel.apply(this, [params]);

        this.urlPreviewText = ko.pureComputed(function() {
            if (this.url()) {
                if (this.url_label && this.url_label()) {
                    return this.url_label();
                } else if (this.url && this.url()) {
                    return this.url();
                }
            }
        }, this);
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: urlDatatypeWidgetTemplate,
    });
    
    return name;
});
