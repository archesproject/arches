define([
    'knockout',
    'viewmodels/concept-select',
    'bindings/select2-query'
], function(ko, ConceptSelectViewModel) {
    return ko.components.register('concept-select-widget', {
        viewModel: function(params) {
            params.configKeys = ['defaultValue'];
            ConceptSelectViewModel.apply(this, [params]);

            var defaultValue = ko.unwrap(this.defaultValue)
            var self = this;

            if (self.configForm){
                self.select2Config.value = self.defaultValue
            };

            if (this.tile && this.tile.tileid() == "" && defaultValue != null && defaultValue != "") {
                this.value(defaultValue);
            };

            if (!self.form) {
                self.value.subscribe(function(val){
                    if (self.defaultValue() != val) {
                        self.defaultValue(val)
                    };
                });
                self.defaultValue.subscribe(function(val){
                    if (self.value() != val) {
                        self.value(val)
                    };
                });
            };
        },
        template: {
            require: 'text!widget-templates/concept-select'
        }
    });
});
