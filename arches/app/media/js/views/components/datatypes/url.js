define([
    'knockout',
    'templates/views/components/datatypes/url.htm',
], function(ko, urlDatatypeTemplate) {
    var name = 'url-datatype-config';
    const viewModel = function(params) {
        var self = this;
         
        this.search = params.search;
        if (this.search) {
            var filter = params.filterValue();
            this.node = params.node;
            this.op = ko.observable(filter.op || '~');
            this.searchValue = ko.observable(filter.val || '');
            this.filterValue = ko.computed(function() {
                return {
                    op: self.op(),
                    val: self.searchValue()
                };
            }).extend({ throttle: 750 });
            params.filterValue(this.filterValue());
            this.filterValue.subscribe(function(val) {
                params.filterValue(val);
            });
        }
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: urlDatatypeTemplate,
    });

    return name;
});
