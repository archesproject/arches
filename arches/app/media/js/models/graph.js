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
        * @param {NodeModel} node - the node to be selected
        */
        selectNode: function(newly_selected_node){
            this.trigger('select-node', newly_selected_node);
            var currentlySelectedNode = this.get('selectedNode')();
            if (currentlySelectedNode && currentlySelectedNode.dirty()) {
                return false;
            }else{
                this.get('nodes')().forEach(function (node) {
                    if(node !== newly_selected_node){
                        node.selected(false);
                    }
                });
                newly_selected_node.selected(true);
                return true;
            }
        },


        /**
         * deleteNode - deletes the passed in node from the db and updates the graph
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node to be deleted
         * @param  {function} callback - (optional) a callback function
         * @param  {object} scope - (optional) the scope used for the callback
         */
        deleteNode: function(node, callback, scope){
            this._doRequest({
                type: "DELETE",
                url: this.url + this.get('graphid') + '/delete_node',
                data: JSON.stringify({nodeid:node.nodeid})
            }, function(response, status){
                if (status === 'success' &&  response.responseJSON) {
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
                    if (node.isCollector()) {
                        this.get('cards').remove(function (card) {
                            return card.nodegroup_id === node.nodeid;
                        });
                    }
                    this.get('edges').remove(function (edge) {
                        return _.contains(edges, edge);
                    });
                    this.get('nodes').remove(function (node) {
                        return _.contains(nodes, node);
                    });
                    parentNode.children.remove(node);
                    parentNode.selected(true);
                }else{
                    this.trigger('error', response, 'deleteNode');
                }

                if (typeof callback === 'function') {
                    scope = scope || this;
                    callback.call(scope, response, status);
                }
            }, this, 'changed');
        },

        /**
         * getParentNode - gets the parent node of the passed in node
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node whose parent should be retrieved
         * @return {object} the parent node of the passed in node
         * If parent node of the passed in node can't be found then reutrn passed in node.
         */
        getParentNode: function(node) {
            var edge = this.get('edges')()
                .find(function (edge) {
                    return edge.rangenode_id === node.nodeid;
                });
            if (edge) {
              return this.get('nodes')()
                  .find(function (node) {
                      return edge.domainnode_id === node.nodeid;
                    });
              } else {
                  return node;
              };
        },

        /**
         * appendBranch - appends a graph onto a specific node within this graph
         * @memberof GraphModel.prototype
         * @param  {string} nodeid - the node id of the node within this graph that we're connecting the branch to
         * @param  {string} property - the ontology property to use to connect the branch, leave null to use the first available property
         * @param  {string} branch_graph - the {@link GraphModel} we're appending to this graph
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        appendBranch: function(nodeid, property, branch_graph, callback, scope){
            property = property ? property : null;
            if(property === null){
                if(this.get('selectedNode')().ontologyclass()){
                    var ontology_connection = _.find(branch_graph.get('domain_connections'), function(domain_connection){
                        return _.find(domain_connection.ontology_classes, function(ontology_class){
                            return ontology_class === this.get('selectedNode')().ontologyclass();
                        }, this)
                    }, this);
                    if(ontology_connection){
                        property = ontology_connection.ontology_property;
                    }else{
                        if (typeof callback === 'function') {
                            scope = scope || self;
                            callback.call(scope, null, 'failed');
                        }
                        return;
                    }
                }
            }

            this._doRequest({
                type: "POST",
                url: this.url + this.get('graphid') + '/append_branch',
                data: JSON.stringify({nodeid:nodeid, property: property, graphid: branch_graph.get('graphid')})
            }, function(response, status){
                if (status === 'success' &&  response.responseJSON) {
                    var branchroot = response.responseJSON.root;
                    response.responseJSON.nodes.forEach(function(node){
                        this.get('nodes').push(new NodeModel({
                            source: node,
                            datatypelookup: this.get('datatypelookup'),
                            graph: this,
                            ontology_namespaces: this.get('root').ontology_namespaces
                        }));
                    }, this);
                    response.responseJSON.edges.forEach(function(edge){
                        this.get('edges').push(edge);
                    }, this);
                    response.responseJSON.nodegroups.forEach(function(nodegroup){
                        this.get('nodegroups').push(nodegroup);
                    }, this);
                    response.responseJSON.cards.forEach(function(card){
                        this.get('cards').push(card);
                    }, this);

                    if(!this.get('isresource')){
                        this.get('nodes')().forEach(function (node) {
                            node.selected(false);
                            if (node.nodeid === branchroot.nodeid){
                                node.selected(true);
                            }
                        });
                    }
                }else{
                    this.trigger('error', response, 'appendBranch');
                }

                if (typeof callback === 'function') {
                    scope = scope || this;
                    callback.call(scope, response, status);
                }
            }, this, 'changed');
        },

        /**
         * appendNode - appends a graph onto a specific node within this graph
         * @memberof GraphModel.prototype
         * @param  {string} nodeid - the node id of the node within this graph that we're connecting the branch to
         * @param  {string} property - the ontology property to use to connect the branch, leave null to use the first available property
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        appendNode: function(node, property, callback, scope){
            var self = this;
            property = property ? property : null;
            // if(property === null){
            //     if(this.get('selectedNode')().ontologyclass()){
            //         var ontology_connection = _.find(branch_graph.get('domain_connections'), function(domain_connection){
            //             return _.find(domain_connection.ontology_classes, function(ontology_class){
            //                 return ontology_class === this.get('selectedNode')().ontologyclass();
            //             }, this)
            //         }, this);
            //         if(ontology_connection){
            //             property = ontology_connection.ontology_property;
            //         }else{
            //             if (typeof callback === 'function') {
            //                 scope = scope || self;
            //                 callback.call(scope, null, 'failed');
            //             }
            //             return;
            //         }
            //     }
            // }

            this._doRequest({
                type: "POST",
                url: this.url + this.get('graphid') + '/append_node',
                data: JSON.stringify({nodeid:node.nodeid, property: property})
            }, function(response, status){
                if (status === 'success' &&  response.responseJSON) {
                    var newNode = new NodeModel({
                        source: response.responseJSON.node,
                        datatypelookup: this.get('datatypelookup'),
                        graph: this,
                        ontology_namespaces: this.get('root').ontology_namespaces
                    })
                    newNode.children = ko.observableArray([]);

                    this.get('nodes').push(newNode);
                    this.get('edges').push(response.responseJSON.edge);
                    node.children.unshift(newNode)
                    // setTimeout(function(){
                    // },500)

                    // response.responseJSON.nodegroups.forEach(function(nodegroup){
                    //     this.get('nodegroups').push(nodegroup);
                    // }, this);

                    if(!this.get('isresource')){
                        this.selectNode(newNode);
                    }
                }else{
                    this.trigger('error', response, 'appendNode');
                }

                if (typeof callback === 'function') {
                    scope = scope || this;
                    callback.call(scope, response, status);
                }
            }, this, 'changed');
        },

        /**
         * moveNode - moves a node from one part of the graph to another
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node within this graph that we're moving
         * @param  {string} property - the ontology property to use to connect the branch
         * @param  {NodeModel} newParentNode - the node to which we moved our branch to
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        moveNode: function(node, property, newParentNode, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + this.get('graphid') + '/move_node',
                data: JSON.stringify({nodeid:node.nodeid, property: property, newparentnodeid: newParentNode.nodeid})
            }, function(response, status){
                if (status === 'success' &&  response.responseJSON) {
                    this.get('edges')().find(function (edge) {
                        if(edge.edgeid === response.responseJSON.edges[0].edgeid){
                            edge.domainnode_id = response.responseJSON.edges[0].domainnode_id;
                            return true;
                        }
                        return false;
                    });
                    this.get('nodes')().forEach(function (node) {
                        found_node = response.responseJSON.nodes.find(function(response_node){
                            return response_node.nodeid === node.nodeid;
                        });
                        if (found_node){
                            node.parse(found_node);
                        }
                    });
                }else{
                    this.trigger('error', response, 'moveNode');
                }

                if (typeof callback === 'function') {
                    scope = scope || this;
                    callback.call(scope, response, status);
                }
            }, this, 'changed');
        },

        /**
         * updateNode - updates the values of a node
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node with updated values
         * @param  {function} callback - the function to call after the response returns from the server
         * @param  {object} scope - the value of "this" in the callback function
         */
        updateNode: function(node, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + this.get('graphid') + '/update_node',
                data: JSON.stringify(node.toJSON())
            }, function(response, status){
                if (status === 'success' &&  response.responseJSON) {
                    _.each(this.get('nodes')(), function(node){
                        var nodeJSON = _.find(response.responseJSON.nodes, function (returned_node) {
                            return node.nodeid === returned_node.nodeid;
                        });
                        node.parse(nodeJSON);
                    }, this);
                }else{
                    this.trigger('error', response, 'updateNode');
                }

                if (typeof callback === 'function') {
                    scope = scope || this;
                    callback.call(scope, response, status);
                }
            }, this, 'changed');
        },

        /**
         * getValidNodesEdges - gets a list of possible ontolgoy properties and classes the node
         * referenced by it's id could be based on the location of the node in the graph
         * @memberof GraphModel.prototype
         * @param  {string} nodeid - the node id of the node of interest
         * @param  {function} callback - function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
         */
        getValidNodesEdges: function(nodeid, callback, scope){
            this._doRequest({
                type: "GET",
                url: this.url + this.get('graphid') + '/get_related_nodes/' + nodeid,
            }, function(response, status){
                callback.call(scope, response.responseJSON);
            }, this);
        },

        /**
         * getValidDomainClasses - gets a list of possible ontolgoy properties and classes the node
         * referenced by it's id could use to be appened to other nodes
         * @memberof GraphModel.prototype
         * @param  {string} nodeid - the node id of the node of interest
         * @param  {function} callback - function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
         */
        getValidDomainClasses: function(nodeid, callback, scope){
            this._doRequest({
                type: "GET",
                url: this.url + this.get('graphid') + '/get_valid_domain_nodes/' + nodeid,
            }, function(response, status){
                callback.call(scope, response.responseJSON);
            }, this);
        },

        /**
         * isType - does this graph contain a card, a collection of cards, or no cards
         * @memberof GraphModel.prototype
         * @return  {string} - either 'card', 'card_collector', or 'undefined'
         */
        isType: function(){
            var nodegroups = [];
            this.get('nodes')().forEach(function (node) {
                if(node.isCollector()){
                    nodegroups.push(node);
                }
            });
            switch(nodegroups.length) {
                case 0:
                    return 'undefined';
                    break;
                case 1:
                    return 'card'
                    break;
                default:
                    return 'card_collector'
            }
        },

        /**
         * canAppend - test to see whether or not a graph can be appened to this graph at a specific location
         * @memberof GraphModel.prototype
         * @param  {object} graphToAppend - the {@link GraphModel} to test appending on to this graph
         * @param  {NodeModel} nodeToAppendTo - the node from which to append the graph, defaults to the graphs selected node
         * @return  {boolean} - true if the graph can be appended, false otherwise
         */
        canAppend: function(graphToAppend, nodeToAppendTo){
            nodeToAppendTo = nodeToAppendTo ? nodeToAppendTo : this.get('selectedNode')();
            var typeOfGraphToAppend = graphToAppend.isType();

            if(!!this.get('ontology_id') && !!graphToAppend.get('ontology_id')){
                var found = !!_.find(graphToAppend.get('domain_connections'), function(domain_connection){
                    return !!_.find(domain_connection.ontology_classes, function(ontology_class){
                        return ontology_class === nodeToAppendTo.ontologyclass();
                    }, this)
                }, this);
                if(!found){
                    return false;
                }
            }

            if(this.get('isresource')){
                if(nodeToAppendTo.nodeid !== this.get('root').nodeid){
                    return false;
                }else{
                    if(typeOfGraphToAppend === 'undefined'){
                        return false;
                    }
                }
            }else{ // this graph is a Graph
                switch(this.isType()) {
                    case 'undefined':
                        return false;
                        break;
                    case 'card':
                        if(typeOfGraphToAppend === 'card'){
                            if(nodeToAppendTo.nodeid === this.get('root').nodeid){
                                if(!(this.isGroupSemantic(nodeToAppendTo))){
                                    return false;
                                }
                            }else{
                                return false;
                            }
                        }
                        else if(typeOfGraphToAppend === 'card_collector'){
                            return false;
                        }
                        break;
                    case 'card_collector':
                        if(typeOfGraphToAppend === 'card_collector'){
                            return false;
                        }
                        if(this.isNodeInChildGroup(nodeToAppendTo)){
                            if(typeOfGraphToAppend === 'card'){
                                return false;
                            }
                        }
                        break;
                }
            }

            return true;
        },

        /**
         * parse - parses the passed in attributes into a {@link GraphModel}
         * @memberof GraphModel.prototype
         * @param  {object} attributes - the properties to seed a {@link GraphModel} with
         */
        parse: function(attributes){
            var self = this;
            var datatypelookup = {};

            attributes =_.extend({datatypes:[], domain_connections:[]}, attributes);

            _.each(attributes.datatypes, function(datatype){
                datatypelookup[datatype.datatype] = datatype;
            }, this)
            this.set('datatypelookup', datatypelookup);

            _.each(attributes.data, function(value, key){
                switch(key) {
                    case 'edges':
                    case 'cards':
                        this.set(key, ko.observableArray(value));
                        break;
                    case 'nodes':
                        var nodes = [];
                        attributes.data.nodes.forEach(function (node, i) {
                            var nodeModel = new NodeModel({
                                source: node,
                                datatypelookup: datatypelookup,
                                graph: self,
                                ontology_namespaces: attributes.ontology_namespaces
                            });
                            nodeModel.children = ko.observableArray([]);
                            if(node.istopnode){
                                this.set('root', nodeModel);
                            }
                            nodes.push(nodeModel);
                        }, this);
                        this.set('nodes', ko.observableArray(nodes));
                        break;
                    case 'root':
                        break;
                    default:
                        this.set(key, value)
                }
            }, this)

            this.tree = this.constructTree(); //ko.pureComputed(this.constructTree, this);

            this.set('selectedNode', ko.computed(function() {
                var selectedNode = _.find(self.get('nodes')(), function(node){
                    return node.selected();
                }, this);
                return selectedNode;
            }));

            var root = this.get('root');
            if(!!root){
                root.selected(true);
            }

            this.graphCards = ko.computed(function(){
                var parentCards = [];
                if (this.get('cards')) {
                    var allCards = this.get('cards')();
                    this.get('nodegroups').filter(function(nodegroup){
                        return !!nodegroup.parentnodegroup_id === false;
                    }, this).forEach(function(nodegroup){
                        parentCards = parentCards.concat(allCards.filter(function(card){
                            return card.nodegroup_id === nodegroup.nodegroupid;
                        }, this))
                    }, this);
                }
                return parentCards;
            }, this);
        },

        /**
         * constructTree - created a hierarchical node listing from the nodes and edges
         * @memberof GraphModel.prototype
         * @return {object} a hierchical node listing
         */
        constructTree: function(){
            var lut = {};
            var sorted = [];
            var edge_map = {};
            var nodes = this.get('nodes')();
            var edges = this.get('edges')();

            function sort(a){
                var len = a.length;
                var fix = -1;
                for (var i = 0; i < len; i++ ){
                    while (!!~(fix = a.findIndex(e => a[i].parent == e.id)) && fix > i)
                        [a[i],a[fix]] = [a[fix],a[i]]; // ES6 swap
                    lut[a[i].id]=i;
                }
                //console.log(lut); //check LUT on the console.
                return a;
            }

            edges.forEach(function(edge){
                edge_map[edge.rangenode_id] = edge.domainnode_id;
            })

            nodes.forEach(function(node){
                if(!ko.isObservable(node.children)){
                    node.children = ko.observableArray([]);
                }else{
                    node.children.removeAll();
                }
                node.parent = edge_map[node.id] ? edge_map[node.id] : '#';
            });

            sorted = sort(nodes.slice(0)); // don't modify things that don't belong to you :)
            for (var i = sorted.length-1; i >= 0; i--){
                if (sorted[i].parent != "#") {
                    sorted[lut[sorted[i].parent]].children.push(sorted.splice(i,1)[0]);
                }
            }
          return sorted;
        },

        /**
         * isNodeInParentGroup - test to see if the node is in a group that is not a child to another group
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node to test
         * @return {Boolean} true if the node is in a parent group, false otherwise
         */
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

        /**
         * isNodeInChildGroup - test to see if the node is in a group that is a child to another group
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node to test
         * @return {Boolean} true if the node is in a child group, false otherwise
         */
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

        /**
         * isGroupSemantic - test to see if all the nodes in a group are semantic
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node to use as a basis of finding the group
         * @return  {boolean} - true if the group contains only semantic nodes, otherwise false
         */
        isGroupSemantic: function(node){
            return _.every(this.getGroupedNodes(node), function(node){
                return node.datatype() === 'semantic';
            }, this)
        },

        /**
         * getGroupedNodes - given a node, get any other nodes that share the same group
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node to use as a basis of finding the group
         * @return  {array} - a list of {@link NodeModel}
         */
        getGroupedNodes: function (node) {
            var nodeGroupId = node.nodeGroupId();
            if (!nodeGroupId) {
                return [node];
            }
            return _.filter(this.get('nodes')(), function(node) {
                return node.nodeGroupId() && node.nodeGroupId() === nodeGroupId;
            })
        },

        /**
         * getParentNodesAndEdges - given a node, get all the parent nodes edges
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node from which to get the node's parents
         * @return  {object} - an object with a list of {@link NodeModel} and edges
         */
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

        /**
         * getChildNodesAndEdges - given a node, get all the child nodes edges
         * @memberof GraphModel.prototype
         * @param  {NodeModel} node - the node from which to get the node's children
         * @return  {object} - an object with a list of {@link NodeModel} and edges
         */
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

        /**
         * _doRequest - a wrapper around a simple ajax call
         * @memberof GraphModel.prototype
         * @param  {object} config - a config object to pass to the ajax request
         * @param  {function} callback - function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
         * @param  {string} eventname - (optional) the event to trigger upon successfull return of the request
         */
        _doRequest: function (config, callback, scope, eventname) {
            var self = this;
            $.ajax($.extend({
                complete: function (request, status) {
                    if (typeof callback === 'function') {
                        callback.call(scope || self, request, status);
                    }
                    if(!!eventname){
                        self.trigger(eventname, self, request);
                    }
                }
            }, config));
        }

    });
});
