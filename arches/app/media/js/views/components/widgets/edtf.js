import ko from 'knockout';
import _ from 'underscore';
import arches from 'arches';
import WidgetViewModel from 'viewmodels/widget';
import edtfTemplate from 'templates/views/components/widgets/edtf.htm';
import 'bindings/key-events-click';


/**
* registers a edtf-widget component for use in forms
* @function external:"ko.components".edtf-widget
* @param {object} params
* @param {string} params.value - the value being managed
* @param {function} params.config - observable containing config object
* @param {string} params.config().label - label to use alongside the text input
* @param {string} params.config().placeholder - default text to show in the text input
*/

const viewModel = function(params) {
    const self = this;
        
    params.configKeys = ['placeholder', 'defaultValue'];
    this.showEDTFFormats = ko.observable(false);
    this.transformedEdtf = ko.observable();
    this.getEdtf = val => {window.fetch(arches.urls.transform_edtf_for_tile + "?value=" + val)
        .then(response => {
            if(response.ok) {
                return response.json();
            } else {
                self.transformedEdtf(null);
            }
        })
        .then(json => {
            if (json?.data?.[1]) {
                self.transformedEdtf(json.data[0]);
            } else {
                self.transformedEdtf(null);
            }
        });
    };
    
    this.getEdtf(ko.unwrap(params.value));
    if (params.state !== 'report') {
        params.value.subscribe(val => {
            self.getEdtf(val);
        });
    }

    WidgetViewModel.apply(this, [params]);
};

export default ko.components.register('edtf-widget', {
    viewModel: viewModel,
    template: edtfTemplate,
});
