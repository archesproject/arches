define([
    'backbone'
], function(Backbone) {
    var ListView = Backbone.View.extend({

        items: [],
        single_select: true,

        initialize: function(options) {
            console.log(options);
        }


    });

    return ListView;
});
