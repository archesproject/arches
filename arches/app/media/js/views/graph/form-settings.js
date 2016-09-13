define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'knockout-mapping',
    'form-settings-data'
], function($, _, Backbone, ko, koMapping, data) {

    var FormSettingsView = Backbone.View.extend({
        /**
        * A backbone view representing a form settings form
        * @augments Backbone.View
        * @constructor
        * @name FormSettingsView
        */

        /**
        * Initializes the view with optional parameters
        * @param {object} options
        * @param {object} options.formModel - a reference to the selected {@link FormModel}
        */
        initialize: function(options) {
            var self = this;
            this.formModel = options.formModel;
            this.iconFilter = ko.observable('');
            this.icons = ko.computed(function () {
                return _.filter(data.icons, function (icon) {
                    return icon.name.indexOf(self.iconFilter()) >= 0;
                });
            })
        }
    });
    return FormSettingsView;
});
