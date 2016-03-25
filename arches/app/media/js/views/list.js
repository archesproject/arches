define([
    'jquery',
    'backbone',
    'knockout',
    'isotope',
    'isotope-packery'
], function($, Backbone, ko, Isotope) {
    var ListView = Backbone.View.extend({

        items: ko.observableArray(),
        single_select: true,

        initialize: function(options) {
            console.log(options);
            var elem = this.$el.find('.grid')[0];
            this.isotopeContainer = new Isotope( elem, {
              // options
              itemSelector: '.grid-item',
              layoutMode: 'packery'
            });

            this.filter = ko.observable('');
            this.filter.subscribe(function(newValue){
                var filter = this.filter().toLowerCase();
                this.items().forEach(function(item){
                    item.filtered(true);
                    if(item.name.toLowerCase().indexOf(filter) !== -1){
                        item.filtered(false);
                    }
                }, this);
            }, this, 'change')

        },

        clearSelection: function(){
            console.log('clear selection')
        },

        clearSearch: function(){
            this.filter('');
        }

    });
    

    return ListView;
});
