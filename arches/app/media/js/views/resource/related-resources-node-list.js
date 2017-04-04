define([
    'knockout',
    'views/list'
], function(ko, ListView) {
    var RelatedResourcesNodeList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name RelatedResourcesNodeList
        */

        /**
        * initializes the view with optional parameters
        * @memberof RelatedResourcesNodeList.prototype
        * @param {object} options
        */
        initialize: function(options) {
            var self = this;
            if (options.items) {
                this.items = options.items;
            }
            if (options.items) {
                this.groups = options.groups;
            }
            var initializeItem = function(item){
                var minimumRelations = self.items().length > 0 ? 1 : 0; //If initialized with multiple nodes, then each node has at least 1 relationship
                if (!item.filtered) {
                    item.filtered = ko.observable(false);
                }
                if (!item.selected) {
                    item.selected = ko.observable(false);
                }
                if (!item.total) {
                    item.total = ko.observable(minimumRelations);
                }
                if (!item.loaded) {
                    item.loaded = ko.observable(minimumRelations);
                }
            }
            this.items.subscribe(function (items) {
                items.forEach(initializeItem, this);
            }, this);
            if(this.filter_function){
                this.filter = ko.observable('');
                this.filter.subscribe(this.filter_function, this, 'change');
                this.filter_function();
            }

            this.selectedItems = ko.computed(function(){
                return this.items().filter(function(item){
                    initializeItem(item);
                    return item.selected();
                }, this);
            }, this);
        }

    });
    return RelatedResourcesNodeList;
});
