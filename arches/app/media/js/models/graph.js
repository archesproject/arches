define(['arches',
    'models/abstract',
    'models/node',
    'knockout',
    'underscore'
], function (arches, AbstractModel, NodeModel, ko, _) {
    return AbstractModel.extend({
        /**
        * A backbone model to manage graph data
        * @augments AbstractModel
        * @constructor
        * @name GraphModel
        */

        url: arches.urls.graph,

        constructor: function(attributes, options){
            options || (options = {});
            options.parse = true;
            AbstractModel.prototype.constructor.call(this, attributes, options);
        },

        /**
        * Flags the passed in node as selected
        * @memberof GraphModel.prototype
        * @param {object} node - the node to be selected
        */
        selectNode: function(node){
            this.trigger('select-node', node);
            var currentlySelectedNode = this.get('selectedNode');
            if (currentlySelectedNode() && currentlySelectedNode().dirty()) {
                return false;
            }else{
                this.get('nodes')().forEach(function (node) {
                    node.selected(false);
                });
                node.selected(true);
                return true;
            }
        },


        /**
         * deleteNode - deletes the passed in node from the db and updates the graph
         * @memberof GraphModel.prototype
         * @param  {object} node - the node to be deleted
         * @param  {function} callback - (optional) a callback function
         * @param  {object} scope - (optional) the scope used for the callback
         */
        deleteNode: function(node, callback, scope){
            node['delete'](function (response, status) {
                var success = (status === 'success');
                if (success) {
                    var parentNode = this.getParentNode(node);
                    var getEdges = function (node) {
                        var edges = this.get('edges')()
                            .filter(function (edge) {
                                return edge.domainnode_id === node.nodeid;
                            });
                        var nodes = edges.map(function (edge) {
                            return this.get('nodes')().find(function (node) {
                                return edge.rangenode_id === node.nodeid;
                            });
                        }, this);
                        nodes.forEach(function (node) {
                            edges = edges.concat(getEdges.call(this, node));
                        }, this);
                        return edges
                    };

                    var edges = getEdges.call(this, node);
                    var nodes = edges.map(function (edge) {
                        return this.get('nodes')().find(function (node) {
                            return edge.rangenode_id === node.nodeid;
                        });
                    }, this);
                    var edge = this.get('edges')()
                        .find(function (edge) {
                            return edge.rangenode_id === node.nodeid;
                        });
                    nodes.push(node);
                    edges.push(edge);
                    this.get('edges').remove(function (edge) {
                        return _.contains(edges, edge);
                    });
                    this.get('nodes').remove(function (node) {
                        return _.contains(nodes, node);
                    });
                    parentNode.selected(true);
                    this.trigger('changed');
                }
                if (typeof callback === 'function') {
                    scope = scope || self;
                    callback.call(scope, response, status);
                }
            }, this);
        },

        /**
         * getParentNode - gets the parent node of the passed in node
         * @memberof GraphModel.prototype
         * @param  {object} node - the node whose parent should be retrieved
         * @return {object} the parent node of the passed in node
         */
        getParentNode: function(node) {
            var edge = this.get('edges')()
                .find(function (edge) {
                    return edge.rangenode_id === node.nodeid;
                });
            return this.get('nodes')()
                .find(function (node) {
                    return edge.domainnode_id === node.nodeid;
                });
        },

        /**
         * appendBranch - appends a graph onto a specific node within this graph
         * @memberof GraphModel.prototype
         * @param  {string} nodeid - the node id of the node within this graph that we're connecting the branch to
         * @param  {string} property - the ontology property to use to connect the branch
         * @param  {string} graphid - the graph id of the branch we're appending to this graph
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        appendBranch: function(nodeid, property, graphid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'append_branch/' + this.get('metadata').graphid,
                data: JSON.stringify({nodeid:nodeid, property: property, graphid: graphid})
            }, function(response, status, self){
                if (status === 'success' &&  response.responseJSON) {
                    var branchroot = response.responseJSON.root;
                    response.responseJSON.nodes.forEach(function(node){
                        self.get('nodes').push(new NodeModel({
                            source: node,
                            datatypelookup: self.get('datatypelookup'),
                            graph: self
                        }));
                    }, this);
                    response.responseJSON.edges.forEach(function(edge){
                        self.get('edges').push(edge);
                    }, this);

                    self.get('nodes')().forEach(function (node) {
                        node.selected(false);
                        if (node.nodeid === branchroot.nodeid){
                            node.selected(true);
                        }
                    });
                }

                if (typeof callback === 'function') {
                    scope = scope || self;
                    callback.call(scope, response, status);
                }
            }, scope, 'changed');
        },

        /**
         * moveNode - moves a node from one part of the graph to another
         * @memberof GraphModel.prototype
         * @param  {object} node - the node within this graph that we're moving
         * @param  {string} property - the ontology property to use to connect the branch
         * @param  {object} newParentNode - the node to which we moved our branch to
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        moveNode: function(node, property, newParentNode, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'move_node/' + this.get('metadata').graphid,
                data: JSON.stringify({nodeid:node.nodeid, property: property, newparentnodeid: newParentNode.nodeid})
            }, function(response, status, self){
                if (status === 'success' &&  response.responseJSON) {
                    self.get('edges')().find(function (edge) {
                        if(edge.edgeid === response.responseJSON.edges[0].edgeid){
                            edge.domainnode_id = response.responseJSON.edges[0].domainnode_id;
                            return true;
                        }
                        return false;
                    });
                    self.get('nodes')().forEach(function (node) {
                        found_node = response.responseJSON.nodes.find(function(response_node){
                            return response_node.nodeid === node.nodeid;
                        });
                        if (found_node){
                            node.nodeGroupId(found_node.nodegroup_id);
                        }
                    });
                }
                if (typeof callback === 'function') {
                    scope = scope || self;
                    callback.call(scope, response, status);
                }
            }, scope, 'changed');
        },

        /**
         * updateNode - updates the values of a node
         * @memberof GraphModel.prototype
         * @param  {object} node - the node with updated values
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        updateNode: function(node, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'update_node/' + this.get('metadata').graphid,
                data: JSON.stringify(node.toJSON())
            }, function(response, status, self){
                if (status === 'success' &&  response.responseJSON) {
                    _.each(self.get('nodes')(), function(node){
                        var nodeJSON = _.find(response.responseJSON.nodes, function (returned_node) {
                            return node.nodeid === returned_node.nodeid;
                        });
                        node.parse(nodeJSON);
                    }, this);
                }
                if (typeof callback === 'function') {
                    scope = scope || self;
                    callback.call(scope, response, status);
                }
            }, scope, 'changed');
        },

        getValidNodesEdges: function(nodeid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + this.get('metadata').graphid + '/get_related_nodes',
                data: JSON.stringify({'nodeid': nodeid})
            }, function(response, status, self){
                callback.call(scope, response.responseJSON);
            }, this);
        },

        getValidDomainClasses: function(nodeid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + this.get('metadata').graphid + '/get_valid_domain_nodes',
                data: JSON.stringify({'nodeid': nodeid})
            }, function(response, status, self){
                callback.call(scope, response.responseJSON);
            }, this);
        },

        parse: function(attributes){
            var self = this;
            var datatypelookup = {};

            attributes =_.extend({data:{'nodes':[], 'edges': []}, datatypes:[]}, attributes);

            _.each(attributes.datatypes, function(datatype){
                datatypelookup[datatype.datatype] = datatype.iconclass;
            }, this)
            this.set('datatypelookup', datatypelookup);

            this.set('edges', ko.observableArray(attributes.data.edges));
            this.set('metadata', attributes.data.metadata);

            attributes.data.nodes.forEach(function (node, i) {
                attributes.data.nodes[i] = new NodeModel({
                    source: node,
                    datatypelookup: datatypelookup,
                    graph: self
                });
                if(node.istopnode){
                    this.set('root', attributes.data.nodes[i]);
                    attributes.data.nodes[i].selected(true);
                }
            }, this);
            this.set('nodes', ko.observableArray(attributes.data.nodes));

            this.set('selectedNode', ko.computed(function() {
                var selectedNode = _.find(self.get('nodes')(), function(node){
                    return node.selected();
                }, this);
                return selectedNode;
            }));
        },

        getParentProperty: function(node){
            var ret;
            this.get('edges')().forEach(function (edge) {
                if (edge.rangenode_id === node.nodeid){
                    ret = edge.ontologyproperty;
                }
            }, this);
            return ret;
        },

        isNodeInParentGroup: function (node) {
            var isInParentGroup = false;
            var nodeGroupId = node.nodeGroupId();
            if (nodeGroupId) {
                var collector = _.find(this.get('nodes')(), function (node) {
                    return node.nodeid === nodeGroupId;
                });
                var childNodesAndEdges = this.getChildNodesAndEdges(collector);
                var childGroupNode = childNodesAndEdges.nodes.find(function(childNode) {
                    return childNode.nodeGroupId() !== nodeGroupId;
                });
                if (childGroupNode) {
                    isInParentGroup = true;
                }
            }
            return isInParentGroup;
        },

        isNodeInChildGroup: function (node) {
            var nodeGroupId = node.nodeGroupId()
            if (!nodeGroupId) {
                return false;
            }
            var parentNodes = this.getParentNodesAndEdges(node).nodes;
            var hasParentGroup = !!parentNodes.find(function (parentNode) {
                parentNodeGroupId = parentNode.nodeGroupId()
                return parentNodeGroupId && parentNodeGroupId !== nodeGroupId;
            });
            return hasParentGroup;
        },

        getGroupedNodes: function (node) {
            var nodeGroupId = node.nodeGroupId();
            if (!nodeGroupId) {
                return [node];
            }
            return _.filter(this.get('nodes')(), function(node) {
                return node.nodeGroupId() && node.nodeGroupId() === nodeGroupId;
            })
        },

        getParentNodesAndEdges: function (node) {
            var self = this;
            var nodes = [];
            var edges = [];
            var edge = self.get('edges')().find(function(edge){
                return edge.rangenode_id === node.nodeid;
            });
            if (edge) {
                var domainnode = self.get('nodes')().find(function(node) {
                    return node.nodeid === edge.domainnode_id;
                });
                nodes.push(domainnode);
                edges.push(edge);

                var nodesAndEdges = self.getParentNodesAndEdges(domainnode);
                nodes = nodes.concat(nodesAndEdges.nodes);
                edges = edges.concat(nodesAndEdges.edges);
            }
            return {
                nodes: nodes,
                edges: edges
            }
        },

        getChildNodesAndEdges: function (node) {
            var self = this;
            var nodes = [];
            var edges = [];
            self.get('edges')().filter(function(edge){
                return edge.domainnode_id === node.nodeid;
            }).forEach(function (edge) {
                var rangenode = self.get('nodes')().find(function(node) {
                    return node.nodeid === edge.rangenode_id;
                });
                nodes.push(rangenode);
                edges.push(edge);

                var nodesAndEdges = self.getChildNodesAndEdges(rangenode);
                nodes = nodes.concat(nodesAndEdges.nodes);
                edges = edges.concat(nodesAndEdges.edges);
            }, self);
            return {
                nodes: nodes,
                edges: edges
            }
        },

        _doRequest: function (config, callback, scope, eventname) {
            var self = this;
            if (! scope){
                scope = self;
            }
            $.ajax($.extend({
                complete: function (request, status) {
                    if (typeof callback === 'function') {
                        callback.call(scope, request, status, self);
                    }
                    if (status === 'success' &&  request.responseJSON) {
                        if(eventname || eventname !== ''){
                            self.trigger(eventname, self);
                        }
                    }
                }
            }, config));
        }

    });
});
