define([
    'backbone',
], function(Backbone) {
    var ReportEditorTree = Backbone.View.extend({
        /**
        * A backbone view representing a tree of report components
        * @augments Backbone.View
        * @constructor
        * @name ReportEditorTree
        */

        /**
        * Initializes the view with optional parameters
        * @memberof ReportEditorTree.prototype
        */
        initialize: function(options) {
            this.report = options.report;
            this.selection = options.selection;
        }
    });
    return ReportEditorTree;
});
