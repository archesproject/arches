define([
    'knockout',
    'underscore',
    'templates/views/components/datatypes/file-list.htm',
], function(ko, _, fileListDatatypeTemplate) {
    var name = 'file-list-datatype-config';
    const viewModel = function(params) {
        const self = this;
        this.config = params.config;
        this.search = params.search;

        if (this.search) {
            var filter = params.filterValue();
            this.op = ko.observable(filter.op || '~');
            this.node = params.node;
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
        } else {
            this.maxFiles = ko.observable(params.config.maxFiles());
            this.maxFiles.subscribe(function(val) {
                var int = parseInt(val);
                if(int > 0) { params.config.maxFiles(int); }
                else { self.maxFiles(1); }
            });

            this.imagesOnly = params.config.imagesOnly;
            params.config.maxFiles.subscribe((val) => self.maxFiles(val));
            this.activated = params.config.activateMax;
        }
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: fileListDatatypeTemplate,
    });

    return name;
});
