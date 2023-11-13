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

        this.maxFiles = ko.observable(params.config.maxFiles());
        this.maxFiles.subscribe(function(val) {
            var int = parseInt(val);
            if(int > 0) { params.config.maxFiles(int); }
            else { self.maxFiles(1); }
        });

        this.imagesOnly = params.config.imagesOnly;
        params.config.maxFiles.subscribe((val) => self.maxFiles(val));
        this.activated = params.config.activateMax;
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: fileListDatatypeTemplate,
    });

    return name;
});
