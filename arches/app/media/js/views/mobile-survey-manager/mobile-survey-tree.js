define([
    'jquery',
    'knockout',
    'underscore',
    'views/tree-view',
    'arches'
], function($, ko, _, TreeView, arches) {
    var loading = ko.observable(false);


    var tree = TreeView.extend({
        filter: ko.observable(''),
        filterFunction: function(){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                item.filtered(true);
                if (filter.length > 2) {
                    if (item.name().toLowerCase().indexOf(filter) !== -1 ||
                            item.datatype().toLowerCase().indexOf(filter) !== -1 ||
                            (!!(item.ontologyclass()) ? item.ontologyclass().toLowerCase().indexOf(filter) !== -1 : false)){
                        item.filtered(false);
                        this.expandParentNode(item);
                    }
                }
            }, this);
        },
        initialize: function(options) {
            this.mobilesurvey = options.mobilesurvey;
            this.items = options.items;
        },
        _initializeItem: function(item){
            if (!item.expanded) {
                item.expanded = ko.observable(item.istopnode);
            }
            TreeView.prototype._initializeItem.apply(this, arguments);
        },
        selectItem: function(node){
            console.log('selecting node', node);
            this.trigger('node-selected', node);
        },
        isChildSelected: function(node){
            console.log(node);
            var isChildSelected = function(parent) {
                var childSelected = false;
                console.log(parent);
                // if (!parent.istopnode) {
                //     parent.childNodes().forEach(function(child) {
                //         if (child && child.selected() || isChildSelected(child)) {
                //             childSelected = true;
                //         }
                //     });
                //     return childSelected;
                // }
            };

            return ko.computed(function() {
                return isChildSelected(node);
            }, this);
        }

    });
    return tree;
});
