define(['knockout'], function (ko) {
    var name = 'string-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.search = params.search;
        },
        template: { require: 'text!datatype-config-templates/string' }
    });
    return name;
});
