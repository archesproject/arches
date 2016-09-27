define([
    'backbone',
    'report-templates'
], function(Backbone, reportLookup) {
    var ReportEditorPreview = Backbone.View.extend({
        /**
        * A backbone view representing a preview of a report
        * @augments Backbone.View
        * @constructor
        * @name ReportEditorPreview
        */

        /**
        * Initializes the view with optional parameters
        * @memberof ReportEditorPreview.prototype
        */
        initialize: function(options) {
            this.reportLookup = reportLookup;
            this.report = options.report;
            this.selection = options.selection;
        }
    });
    return ReportEditorPreview;
});
