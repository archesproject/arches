define(['knockout',
    'underscore',
    'arches',
    'viewmodels/widget'
], function(ko, _, arches, WidgetViewModel) {
    /**
    * registers a edtf-widget component for use in forms
    * @function external:"ko.components".edtf-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('edtf-widget', {
        viewModel: function(params) {
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
            }
            
            this.getEdtf(params.value())
            if (params.state !== 'report') {
                params.value.subscribe(val => {
                    self.getEdtf(val);
                })
            }

            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/edtf' }
    });
});
