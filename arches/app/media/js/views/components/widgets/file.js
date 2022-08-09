define([
    'jquery',
    'knockout',
    'underscore',
    'dropzone',
    'uuid',
    'viewmodels/file-widget',
    'templates/views/components/widgets/file.htm',
    'bindings/dropzone',
], function($, ko, _, Dropzone, uuid, FileWidgetViewModel, fileWidgetTemplate) {
    /**
     * registers a file-widget component for use in forms
     * @function external:"ko.components".file-widget
     * @param {object} params
     * @param {string} params.value - the value being managed
     * @param {function} params.config - observable containing config object
     * @param {string} params.config().acceptedFiles - accept attribute value for file input
     * @param {string} params.config().maxFilesize - maximum allowed file size in MB
     */

    const viewModel = function(params) {
        params.configKeys = ['acceptedFiles', 'maxFilesize'];
         
        FileWidgetViewModel.apply(this, [params]);
    };

    return ko.components.register('file-widget', {
        viewModel: viewModel,
        template: fileWidgetTemplate,
    });
});
