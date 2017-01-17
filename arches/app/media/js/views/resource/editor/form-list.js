define([
    'views/list'
], function(ListView) {
    var FormList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name FormList
        */

        filter_function: null,

        /**
        * initializes the view with optional parameters
        * @memberof FormList.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            var unique_forms = _.uniq(options.forms(), function(form){
                return form.formid;
            });
            this.items(unique_forms);
            this.items.sort(function (w, ww) {
                return w.sortorder > ww.sortorder;
            });
            ListView.prototype.initialize.apply(this, arguments);
        }

    });
    return FormList;
});
