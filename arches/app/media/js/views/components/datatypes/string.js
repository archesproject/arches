define([
    'knockout',
    'arches',
    'templates/views/components/datatypes/string.htm',
], function(ko, arches, stringDatatypeTemplate) {
    var name = 'string-datatype-config';
    const viewModel = function(params) {
        var self = this;
         
        this.search = params.search;
        if (this.search) {
            var filter = params.filterValue();
            this.op = ko.observable(filter.op || '~');
            this.node = params.node;
            this.languages = ko.observableArray(arches.languages);
            this.language = ko.observable(arches.activeLanguage);
            this.searchValue = ko.observable(filter.val || '');
            this.filterValue = ko.computed(function() {
                return {
                    op: self.op(),
                    lang: self.language(),
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
        template: stringDatatypeTemplate,
    });
    
    return name;
});
