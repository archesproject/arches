define([
    'underscore',
    'knockout',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, data) {
    var currentWidth, start;
    var viewModel = {
        graphid: ko.observable(data.graphid)
    }

    return new BaseManagerView({
        viewModel: viewModel
    });
});
