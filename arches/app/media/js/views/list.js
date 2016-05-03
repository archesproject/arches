define([
    'jquery',
    'backbone',
    'knockout'
], function($, Backbone, ko) {
    var ListView = Backbone.View.extend({

        items: ko.observableArray(),
        single_select: true,
        filter_function: function(newValue){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                var name = typeof item.name === 'string' ? item.name : item.name();
                item.filtered(true);
                if(name.toLowerCase().indexOf(filter) !== -1){
                    item.filtered(false);
                }
            }, this);
        },

        initialize: function(options) {
            this.filter = ko.observable('');
            this.filter.subscribe(this.filter_function, this, 'change');
        },

        selectItem: function(item, evt){
            var selectedStatus = item.selected();
            if(this.single_select){
                this.clearSelection();
            }
            item.selected(!selectedStatus);
        },

        clearSelection: function(){
            this.items().forEach(function(item){
                item.selected(false);
            }, this);
        },

        clearSearch: function(){
            this.filter('');
        }
    });

    return ListView;
});
