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
        selectItem: function(node){
            // if (!this.graphSettings.dirty()) {
            //     this.graphModel.selectNode(node);
            //     this.trigger('node-selected', node);
            // }
        },
        isChildSelected: function(node) {
            var isChildSelected = function(parent) {
                var childSelected = false;
                if (!parent.istopnode) {
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
