define(['knockout', 'templates/views/components/datatypes/boolean.htm'], function(ko, booleanTemplate) {
    var name = 'boolean-datatype-config';

    const viewModel = function(params) {
        var self = this;
        var config = params.config ? params.config : params.node.config;

         
        this.search = params.search;
        this.graph = params.graph;
        this.trueLabel = config.trueLabel;
        this.falseLabel = config.falseLabel;

        if (this.search) {
            var filter = params.filterValue();
            this.node = params.node;
            this.searchValue = ko.observable(filter.val || '');
            this.filterValue = ko.computed(function() {
                return {
                    val: self.searchValue()
                };
            });
            params.filterValue(this.filterValue());
            this.filterValue.subscribe(function(val) {
                params.filterValue(val);
            });
        }
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: booleanTemplate,
    });

    return name;
});
