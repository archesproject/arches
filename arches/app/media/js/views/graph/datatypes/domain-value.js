define(['arches', 'knockout'], function (arches, ko) {
    ko.components.register('domain-value-datatype-config', {
        viewModel: function(params) {
            this.options = params.config.options;
        },
        template: { require: 'text!datatype-config-templates/domain-value' }
    });
    return name;
});
