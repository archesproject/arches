define([
    'jquery',
    'knockout',
    'underscore',
    'views/tree-view'
], function($, ko, _, TreeView) {
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
            this.activepage = options.activepage;
            this.selectednode = options.selectednode;
            this.status = options.status;
        },
        _initializeItem: function(item){
            if (!item.expanded) {
                item.expanded = ko.observable(item.istopnode);
            }
            TreeView.prototype._initializeItem.apply(this, arguments);
        },
        selectItem: function(selectednode, childnodes){
            var self = this;
            var nodes;
            if (childnodes.length) {
                nodes = childnodes;
            } else {
                nodes = this.items;
            }
            nodes.forEach(function(node){
                ko.unwrap(node.id) === ko.unwrap(selectednode.id) ? node.selected(true) : node.selected(false);
                if (node.selected() === true) {
                    self.activepage(node.pageid || node.id);
                    self.selectednode(node);
                }
                nodes = node.childNodes();
                if (nodes.length > 0) {
                    self.selectItem(selectednode, nodes);
                }
            });
            return;
        },
        isChildSelected: function(node){
            var isChildSelected = function(parent) {
                var childSelected = false;
                if (!parent.istopnode) {
                    parent.childNodes().forEach(function(child) {
                        if (child && child.selected() || isChildSelected(child)) {
                            childSelected = true;
                        }
                    });
                    return childSelected;
                }
            };

            return ko.computed(function() {
                return isChildSelected(node);
            }, this);
        }

    });
    return tree;
});
