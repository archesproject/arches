define([
    'backbone',
    'widgets'
], function(Backbone) {
    var ReportEditorForm = Backbone.View.extend({
        /**
        * A backbone view representing a form for editing report components
        * @augments Backbone.View
        * @constructor
        * @name ReportEditorForm
        */

        /**
        * Initializes the view with optional parameters
        * @memberof ReportEditorForm.prototype
        */
        initialize: function(options) {
            this.report = options.report;
            this.selection = options.selection;
        }
    });
    return ReportEditorForm;
});
