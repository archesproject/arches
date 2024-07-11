define([
    'knockout', 
    'viewmodels/widget',
    'templates/views/components/widgets/urldatatype.htm',
], function(ko, WidgetViewModel, urlDatatypeWidgetTemplate) {
    var name = 'urldatatype';
    const viewModel = function(params) {
        const self = this;
        params.configKeys = ['url_placeholder','url_label_placeholder','link_color'];
        params.valueProperties = ['url', 'url_label'];

        WidgetViewModel.apply(this, [params]);

        // #10027 assign this.url & this.url_label with value versions for updating UI with edits
        if (ko.isObservable(this.value)) {
        
            if (this.value()) {
                var valueUrl = this.value().url;
                var valueUrlLabel = this.value().url_label;
                this.url(valueUrl);
                this.url_label(valueUrlLabel);
            }
            this.value.subscribe(function(newValue) {
                if (newValue) {
                    if (newValue.url) {
                        self.url(newValue.url);
                    } else {
                        self.url("");
                    }
                    if (newValue.url_label) {
                        self.url_label(newValue.url_label);
                    } else {
                        self.url_label("");
                    }
                } else {
                    self.url("");
                    self.url_label("");
                }
            });
        }

        this.urlPreviewText = ko.pureComputed(function() {
            if(self.url()){
                if (self.url_label && self.url_label()) {
                    return self.url_label();
                } else if (self.url && self.url()) {
                    return self.url();
                }
            }
            else{
                return "--";
            }
        }, this);
        
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: urlDatatypeWidgetTemplate,
    });
    
    return name;
});
