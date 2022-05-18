define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('sample-widget', {
        viewModel: function(params) {
            params.configKeys = ['x_placeholder','y_placeholder'];
            WidgetViewModel.apply(this, [params]);
            var self = this;
            if (this.value()) {
                var coords = this.value().split('POINT(')[1].replace(')','').split(' ')
                var srid = this.value().split(';')[0].split('=')[1]
                this.x_value = ko.observable(coords[0]);
                this.y_value = ko.observable(coords[1]);
                this.srid = ko.observable('4326');
            } else {
                this.x_value = ko.observable();
                this.y_value = ko.observable();
                this.srid = ko.observable('4326');
            };

            this.preview = ko.pureComputed(function() {
                var res = "SRID=" + this.srid() + ";POINT(" + this.x_value() + " " + this.y_value() + ")"
                this.value(res);
                return res;
            }, this);
        },
        template: { require: 'text!templates/views/components/widgets/sample-widget.htm' }
    });
});
