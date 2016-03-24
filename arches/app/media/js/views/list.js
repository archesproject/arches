define([
    'jquery',
    'backbone',
    'isotope',
    'isotope-packery'
], function($, Backbone, Isotope) {
    var ListView = Backbone.View.extend({

        items: [],
        single_select: true,

        initialize: function(options) {
            console.log(options);
            var elem = document.querySelector('.grid');
            var iso = new Isotope( elem, {
              // options
              itemSelector: '.grid-item',
              layoutMode: 'packery'
            });
        }


    });
    

    return ListView;
});
