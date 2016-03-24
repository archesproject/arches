define([
    'views/list'
], function(ListView) {
    var NodeList = ListView.extend({

        single_select: false,

        initialize: function(options) {
            this.items = options.nodes;
        }

    });
    return NodeList;
});
