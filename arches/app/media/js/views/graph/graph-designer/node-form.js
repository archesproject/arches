define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'arches',
    'views/components/simple-switch',
    'bindings/chosen'
], function($, _, Backbone, ko, arches) {
    var NodeFormView = Backbone.View.extend({
        /**
        * A backbone view representing a node form
        * @augments Backbone.View
        * @constructor
        * @name NodeFormView
        */

        /**
        * Initializes the view with optional parameters
        * @memberof NodeFormView.prototype
        * @param {object} options
        * @param {object} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            var self = this;
            _.extend(this, _.pick(options, 'graphModel'));
            this.datatypes = _.keys(this.graphModel.get('datatypelookup'));
            this.node = options.node;
            this.isExportable = ko.observable(null);

            this.graph = options.graph;
            this.loading = options.loading || ko.observable(false);
            this.hasOntology = ko.computed(function(){
                return self.graph.ontology_id() === null ? false : true;
            });
            this.isResourceTopNode = ko.computed(function() {
                var node = self.node();
                return self.graphModel.get('isresource') && node && node.istopnode;
            });
            this.restrictedNodegroups = options.restrictedNodegroups;
            this.appliedFunctions = options.appliedFunctions;
            this.primaryDescriptorFunction = options.primaryDescriptorFunction;

            this.isFuncNode = function() {
                var node = self.node();
                var primaryDescriptorNodes = {}, descriptorType = null, pdFunction = this.primaryDescriptorFunction;

                if (!pdFunction || !pdFunction())
                    return false;

                ['name', 'description'].forEach(function(descriptor){
                    try {
                        primaryDescriptorNodes[pdFunction()['config']['descriptor_types'][descriptor]['nodegroup_id']] = descriptor;
                    } catch (e)
                    {
                        // Descriptor doesn't exist so ignore the exception
                        console.log("No descriptor configuration for "+descriptor);
                    }
                });

                [node].concat(!!node['childNodes']() ? node['childNodes']() : [])
                    .find(nodeToCheck => !!(descriptorType = primaryDescriptorNodes[nodeToCheck['id']]));

                return !descriptorType ? false :
                    (descriptorType === "name" ?
                        "This node participates in the name function" :
                        "This node participates in the descriptor function"
                    );
            };

            /**
            * Checks if a node's card is editable and returns a boolean useful
            * in disabling node properties not to be changed in cards/nodegroups with data saved against them.
            * @memberof NodeFormView.prototype
            * @return {boolean}
            */
            this.checkIfImmutable = function() {
                var isImmutable = _.contains(this.restrictedNodegroups, self.node().nodeGroupId());
                return isImmutable;
            };

            this.extendNode = function(node, parameters)
            {
                return _.extend(node, parameters);
            };

            this.toggleRequired = function() {
                var isImmutable = self.checkIfImmutable();
                if (isImmutable === false) {
                    self.node().isrequired(!self.node().isrequired());
                }
            };

            this.disableDatatype = ko.computed(function() {
                var isImmutable = false;
                var node = self.node();
                if (node) {
                    isImmutable = self.checkIfImmutable();
                }
                return self.isResourceTopNode() || isImmutable;
            });

            this.displayMakeCard = ko.computed(function() {
                var res = true;
                if (self.node() && self.graphModel.get('isresource')) {
                    var parentNode = self.graphModel.getParentNode(self.node());
                    if (parentNode.istopnode === true) {
                        res = false;
                    }
                }
                return res;
            });

            this.disableIsCollector = ko.computed(function() {
                var node = self.node();
                var isCollector = false;
                var isNodeInChildGroup = false;
                var hasNonSemanticParentNodes = false;
                var isInParentGroup = false;
                var groupHasNonSemanticNodes = false;
                var hasDownstreamCollector = false;
                if (node) {
                    isCollector = node.isCollector();
                    isNodeInChildGroup = self.graphModel.isNodeInChildGroup(node);
                    var groupNodes = self.graphModel.getGroupedNodes(node);
                    var childNodes = self.graphModel.getChildNodesAndEdges(node).nodes;
                    childNodes.push(node);
                    var parentGroupNodes = _.difference(groupNodes, childNodes);
                    hasNonSemanticParentNodes = !!_.find(parentGroupNodes, function(node) {
                        return node.datatype() !== 'semantic';
                    });
                    groupHasNonSemanticNodes = !!_.find(groupNodes, function(node) {
                        return node.datatype() !== 'semantic';
                    });
                    hasDownstreamCollector = !!_.find(childNodes, function(node) {
                        return node.isCollector();
                    });
                    isInParentGroup = self.graphModel.isNodeInParentGroup(node);
                }
                return self.isResourceTopNode() ||
                    (!isCollector && (isNodeInChildGroup || hasNonSemanticParentNodes)) ||
                    (!isCollector && isInParentGroup && hasDownstreamCollector) ||
                    (isCollector && groupHasNonSemanticNodes && (isInParentGroup || isNodeInChildGroup)) ||
                    (self.graphModel.get('nodes')().length > 1 && node && node.istopnode);
            });
        },

        /**
         * Resets the edited model
         * @memberof NodeFormView.prototype
         */
        cancel: function() {
            this.node().reset();
        },


        /**
         * Calls an async method on the graph model based on the passed in
         * method name.
         * Manages showing loading mask & failure alert
         * @memberof NodeFormView.prototype
         *
         * @param  {string} methodName - method to call on the graph model
         */
        callAsync: function(methodName) {
            var self = this;
            this.loading(true);
            this.graphModel[methodName](this.node(), function(){
                self.loading(false);
            });
        },

        /**
         * Calls the updateNode method on the graph model for the edited node
         * @memberof NodeFormView.prototype
         */
        save: function() {
            this.callAsync('updateNode');
        },

        /**
         * Calls the deleteNode method on the graph model for the edited node
         * @memberof NodeFormView.prototype
         */
        deleteNode: function() {
            this.callAsync('deleteNode');
        },

        /**
         * Calls the toggleIsCollector method on the node model
         * @memberof NodeFormView.prototype
         */
        toggleIsCollector: function() {
            if (this.checkIfImmutable() === false) {
                this.node().toggleIsCollector();
            }
        }
    });
    return NodeFormView;
});
