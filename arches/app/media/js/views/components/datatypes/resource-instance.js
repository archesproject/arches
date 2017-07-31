define(['knockout'], function (ko) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            if (this.search) {

            }
        },
        template: { require: 'text!datatype-config-templates/resource-instance' }
    });
    return name;
});
