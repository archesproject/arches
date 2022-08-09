define([
    'views/list'
], function(ListView) {
    var AppliedFunctionList = ListView.extend({
        /**
        * A backbone view to manage a list of functions
        * @augments ListView
        * @constructor
        * @name AppliedFunctionList
        */

        filterFunction: null,

        /**
        * initializes the view with optional parameters
        * @memberof AppliedFunctionList.prototype
        * @param {object} options
        */
        initialize: function(options) {
            this.items = options.functions;
            this.items.sort(function(left, right) {
                return left.function.name().toLowerCase() == right.function.name().toLowerCase() ? 0 : (left.function.name().toLowerCase() < right.function.name().toLowerCase() ? -1 : 1);
            });
            ListView.prototype.initialize.apply(this, arguments);
        }

    });
    return AppliedFunctionList;
});
