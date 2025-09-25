import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import Dropzone from 'dropzone';
import uuid from 'uuid';
import FileWidgetViewModel from 'viewmodels/file-widget';
import fileWidgetTemplate from 'templates/views/components/widgets/file.htm';
import 'bindings/dropzone';


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

export default ko.components.register('file-widget', {
    viewModel: viewModel,
    template: fileWidgetTemplate,
});
