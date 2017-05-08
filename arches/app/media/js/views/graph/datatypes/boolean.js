define(['knockout'], function (ko) {
    var name = 'boolean-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            if (this.search) {
                this.filter = params.filterValue();
            }
        },
        template: { require: 'text!datatype-config-templates/boolean' }
    });
    return name;
});
