define(['knockout', 'viewmodels/widget'], function(ko, WidgetViewModel) {
    var name = 'urldatatype';
    ko.components.register(name, {
        viewModel: function(params) {
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
        },
        template: { require: 'text!templates/views/components/widgets/urldatatype.htm' }
    });
    return name;
});
