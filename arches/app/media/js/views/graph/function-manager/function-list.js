define([
    'views/list'
], function(ListView) {
    var FunctionList = ListView.extend({
        /**
        * A backbone view to manage a list of functions
        * @augments ListView
        * @constructor
        * @name FunctionList
        */

        filterFunction: null,

        /**
        * initializes the view with optional parameters
        * @memberof FunctionList.prototype
        * @param {object} options
        * @param {object} options.functions - a list of {@link FunctionModel} models
        */
        initialize: function(options) {
            this.items = options.functions;
            this.items.sort(function(left, right) {
                return left.name().toLowerCase() == right.name().toLowerCase() ? 0 : (left.name().toLowerCase() < right.name().toLowerCase() ? -1 : 1);
            });
            ListView.prototype.initialize.apply(this, arguments);
        }

    });
    return FunctionList;
});
