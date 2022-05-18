define([
    'knockout', 
    'utils/report',
    'arches',
    'viewmodels/widget',
    'bindings/codemirror'
], function(ko, reportUtils, arches) {
    return ko.components.register('views/components/reports/scenes/json', {
        viewModel: function(params) {
            var self = this;

            Object.assign(self, reportUtils);
            self.selectedJSON = ko.observable();
            self.selectedFormat = ko.observable();
            self.codeMirrorJsonLDMode = ko.observable();
            self.codeMirrorJsonMode = ko.observable();
            self.resourceInstanceId = params.resourceInstanceId;
            self.json = {};
            self.visible = {
                json: ko.observable(true)
            };

            self.setSelectedJson = async (format) => {
                if(!self.json[format]){
                    const response = await fetch(`${arches.urls.api_resources(self.resourceInstanceId)}?format=${format}`);
                    self.json[format] = await response.json();
                }
                self.selectedJSON(JSON.stringify(self.json[format], null, 2));
                self.selectedFormat(format);
                (format == 'json-ld' ? self.codeMirrorJsonLDMode(true) && self.codeMirrorJsonMode(false) : self.codeMirrorJsonLDMode(false) && self.codeMirrorJsonMode(true));
            };
            self.setSelectedJson('json');
        },
        template: {
            require: 'text!templates/views/components/reports/scenes/json.htm'
        }
    });
});
