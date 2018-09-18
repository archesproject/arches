define(['knockout'], function (ko) {
    var name = 'boolean-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            this.graph = params.graph;

            this.trueLabel = params.config ? params.config.trueLabel : params.node.config.trueLabel;
            this.falseLabel = params.config ? params.config.falseLabel : params.node.config.falseLabel;

            if (this.search) {
                var filter = params.filterValue();
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function () {
                    return {
                        val: self.searchValue()
                    }
                });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function (val) {
                    params.filterValue(val);
                });
            }
        },
        template: { require: 'text!datatype-config-templates/boolean' }
    });
    return name;
});
