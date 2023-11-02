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
        });

        this.imagesOnly = ko.observable(params.config.imagesOnly());
        this.imagesOnly.subscribe(function(val) {
            params.config.imagesOnly(val);
        });

        params.config.imagesOnly.subscribe((val) => self.imagesOnly(val));
        this.activated = params.config.activateMax;
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: fileListDatatypeTemplate,
    });

    return name;
});
