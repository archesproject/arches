define(['knockout'], function (ko) {
    var name = 'concept-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.topConcept = params.config.topConcept;
        },
        template: { require: 'text!datatype-config-templates/concept' }
    });
    return name;
});
