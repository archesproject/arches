define([
    'jquery',
    'knockout',
    'underscore',
    'views/tree-view',
    'arches'
], function($, ko, _, TreeView, arches) {
    var loading = ko.observable(false);

    var GraphTree = TreeView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments TreeView
        * @constructor
        * @name GraphTree
        */

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

        filterEnterKeyHandler: function(context, e) {
            var self = this;
            if (e.keyCode === 13) {
                var highlightedItems = _.filter(this.items(), function(item) {
                    return !item.filtered();
                });
                var previousItem = self.scrollTo();
                self.scrollTo(null);
                if (highlightedItems.length > 0) {
                    var scrollIndex = 0;
                    var previousIndex = highlightedItems.indexOf(previousItem);
                    if (previousItem && highlightedItems[previousIndex+1]) {
                        scrollIndex = previousIndex + 1;
                    }
                    self.scrollTo(highlightedItems[scrollIndex]);
                }
                return false;
            }
            return true;
        },

        /**
        * initializes the view with optional parameters
        * @memberof GraphTree.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            var self = this;
            this.graphModel = options.graphModel;
            this.graphSettings = options.graphSettings;
            this.cardTree = options.cardTree;
            this.appliedFunctions = options.appliedFunctions;
            this.primaryDescriptorFunction = options.primaryDescriptorFunction;
            this.permissionTree = options.permissionTree;
            this.items = this.graphModel.get('nodes');
            this.branchListVisible = ko.observable(false);
            this.scrollTo = ko.observable();
            this.restrictedNodegroups = options.restrictedNodegroups;
            this.showIds = ko.observable(false);
            this.toggleIds = function() {
                self.showIds(!self.showIds());
            };
            TreeView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Returns a knockout computed used to calculate display name of the node
        * @memberof GraphTree.prototype
        * @param {object} node - a node in the tree
        */

        getDisplayName: function(node) {
            return ko.computed(function(){
                var name = node.name();
                if (node.ontologyclass_friendlyname() != "") {
                    name = name + ' (' + node.ontologyclass_friendlyname().split('_')[0] + ')';
                }
                return name;
            }, this);
        },

        /**
         * Returns a boolean to indicate whether this node participates in descriptor function
         * @param {object} node - a node in the tree
         */
        isFuncNode: function(node) {
            var primaryDescriptorNodes = {}, descriptorType, pdFunction = this.primaryDescriptorFunction;

            if(!this.primaryDescriptorFunction())
                return null;

            ['name', 'description'].forEach(function(descriptor) {
                try {
                    primaryDescriptorNodes[pdFunction()['config']['descriptor_types'][descriptor]['nodegroup_id']] = descriptor;
                } catch (e) {
                    // Descriptor doesn't exist so ignore the exception
                    console.log("No descriptor configuration for "+descriptor);
                }
            });

            [node].concat(!!node['childNodes']() ? node['childNodes']() : [])
                .find(nodeToCheck => !!(descriptorType = primaryDescriptorNodes[nodeToCheck['id']]));

            return !!descriptorType;
        },

        /**
        * Returns a knockout computed used to calculate display name of the node
        * @memberof GraphTree.prototype
        * @param {object} node - a node in the tree
        */
        isChildSelected: function(node) {
            var isChildSelected = function(parent) {
                var childSelected = false;
                if (!parent.istopnode) {
                    parent.childNodes().forEach(function(child) {
                        if (child && child.selected() || isChildSelected(child)){
                            childSelected = true;
                        }
                    });
                    return childSelected;
                }
            };

            return ko.computed(function() {
                return isChildSelected(node);
            }, this);
        },

        /**
        * Expands the parent of the passed in node
        * @memberof GraphTree.prototype
        * @param {object} node - the child of the parent node to be expanded
        */
        expandParentNode: function(node) {
            if(node.parent) {
                node.parent.expanded(true);
                this.expandParentNode(node.parent);
            }
        },

        /**
        * Selects the passed in node
        * @memberof GraphTree.prototype
        * @param {object} node - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} e - click event object
        */
        selectItem: function(node){
            if (!this.graphSettings.dirty()) {
                this.graphModel.selectNode(node);
                this.trigger('node-selected', node);
            }
        },

        toggleBranchList: function(node, e) {
            e.stopImmediatePropagation();
            this.branchListVisible(!this.branchListVisible());
            if(this.branchListVisible()){
                node.expanded(true);
            }
            this.trigger('toggle-branch-list');
        },

        addChildNode: function(node, e) {
            e.stopImmediatePropagation();
            this.graphModel.appendNode(node ,function(response, status){
                if(status === 'success') {
                    node.expanded(true);
                    if (node.istopnode && this.graphModel.get('isresource')) {
                        this.cardTree.addCard(response.responseJSON);
                        this.permissionTree.addCard(response.responseJSON);
                    }
                }
            }, this);
        },

        deleteNode: function(node, e) {
            e.stopImmediatePropagation();

            $(e.target).tooltip('destroy');  // needs to be called before the node is deleted

            this.graphModel.deleteNode(node, function(_response, status) {
                if (status === 'success') {
                    if (node.isCollector()) {
                        this.cardTree.deleteCard(node.nodeGroupId());
                        this.permissionTree.deleteCard(node.nodeGroupId());
                    }
                }
            }, this);
        },

        exportBranch: function(node, e) {
            e.stopImmediatePropagation();
            this.graphModel.exportBranch(node, function(response) {
                var url = arches.urls.graph_designer(response.responseJSON.graphid);
                window.open(url);
            });
        },

        beforeMove: function(e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        },
        reorderNodes: function(e) {
            loading(true);
            var nodes = _.map(e.sourceParent(), function(node) {
                return node.attributes.source;
            });
            $.ajax({
                type: "POST",
                data: JSON.stringify({
                    nodes: nodes
                }),
                url: arches.urls.reorder_nodes,
                complete: function() {
                    loading(false);
                }
            });
        },

        _initializeItem: function(item){
            if (!item.expanded) {
                item.expanded = ko.observable(item.istopnode);
            }
            TreeView.prototype._initializeItem.apply(this, arguments);
        },

        collapseAll: function(){
            this.items().forEach(function(item){
                if (!item.istopnode) {
                    item.expanded(false);
                }
            }, this);
        }
    });
    return GraphTree;
});
