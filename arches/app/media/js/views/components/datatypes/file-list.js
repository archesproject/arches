define([
    'knockout',
    'underscore',
    'view-data'
], function (ko, _, data) {
    var name = 'file-list-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.config = params.config;
            this.search = params.search;
            this.maxFiles = ko.observable(params.config.maxFiles());
            this.maxFiles.subscribe(function(val) {
                var int = parseInt(val);
                if(int > 0) { params.config.maxFiles(int); }
            });
            this.activated = params.config.activateMax;
        },
        template: { require: 'text!datatype-config-templates/file-list' }
    });
    return name;
});
