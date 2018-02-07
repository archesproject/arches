define([
    'jquery',
    'underscore',
    'backbone',
    'knockout'
], function($, _, Backbone, ko) {
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
        * @param {object} options.icons - an array of objects representing icons
        */
        initialize: function(options) {
            var self = this;
            this.formModel = options.formModel;
            this.iconFilter = ko.observable('');
            this.icons = ko.computed(function () {
                return _.filter(options.icons, function (icon) {
                    return icon.name.indexOf(self.iconFilter()) >= 0;
                });
            })
        }
    });
    return FormSettingsView;
});
