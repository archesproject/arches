define([
    'knockout',
    'underscore',
    'arches',
    'templates/views/components/datatypes/file-list.htm',
], function(ko, _, arches, fileListDatatypeTemplate) {
    var name = 'file-list-datatype-config';
    const viewModel = function(params) {
        this.config = params.config;
        this.search = params.search;
        this.translations = arches.translations;
        this.maxFiles = ko.observable(params.config.maxFiles());
        this.maxFiles.subscribe(function(val) {
            var int = parseInt(val);
            if(int > 0) { params.config.maxFiles(int); }
        });
        this.activated = params.config.activateMax;
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: fileListDatatypeTemplate,
    });

    return name;
});
