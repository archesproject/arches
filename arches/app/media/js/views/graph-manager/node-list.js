define([
    'views/list'
], function(ListView) {
    var NodeList = ListView.extend({

        single_select: false,

        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            this.items = options.graphModel.get('nodes');
        }

    });
    return NodeList;
});
