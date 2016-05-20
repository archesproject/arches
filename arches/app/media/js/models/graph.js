define(['arches',
    'models/abstract',
    'models/node',
    'knockout',
    'underscore'
], function (arches, AbstractModel, NodeModel, ko, _) {
    return AbstractModel.extend({
        url: arches.urls.graph,

        constructor: function(attributes, options){
            options || (options = {});
            options.parse = true;
            AbstractModel.prototype.constructor.call(this, attributes, options);
        },

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

        deleteNode: function(node, callback, scope){            
            var self = this;
            this._doRequest({
                type: "POST",
                url: this.url + 'update_node/' + this.get('metadata').graphid,
                data: JSON.stringify(node.toJSON())
            }, function(response, status){

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
                this.trigger('changed');
                callback.call(scope, response, status);
            }, scope, 'changed');
        },

        appendBranch: function(nodeid, property, branchmetadatid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'append_branch/' + this.get('metadata').graphid,
                data: JSON.stringify({nodeid:nodeid, property: property, graphid: branchmetadatid})
            }, function(response, status, self){
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


                callback();
            }, scope, 'changed');
        },

        moveNode: function(node, property, newParentNode, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'move_node/' + this.get('metadata').graphid,
                data: JSON.stringify({nodeid:node.nodeid, property: property, newparentnodeid: newParentNode.nodeid})
            }, function(response, status, self){
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
                callback();
            }, scope, 'changed');
        },

        updateNode: function(node, callback, scope){
            var self = this;
            this._doRequest({
                type: "POST",
                url: this.url + 'update_node/' + this.get('metadata').graphid,
                data: JSON.stringify(node.toJSON())
            }, function(response, status){
                _.each(self.get('nodes')(), function(node){
                    var nodeJSON = _.find(response.responseJSON.nodes, function (returned_node) {
                        return node.nodeid === returned_node.nodeid;
                    });
                    var nodeGroup = _.find(response.responseJSON.nodegroups, function (returned_nodegroup) {
                        return node.nodeid === returned_nodegroup.nodegroupid;
                    });
                    nodeJSON.cardinality = nodeGroup?nodeGroup.cardinality:null;
                    node.parse(nodeJSON);
                }, this);
                callback.call(scope, response, status);
            }, scope, 'changed');
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
            attributes.data.nodes.forEach(function (node, i) {
                attributes.data.nodes[i] = new NodeModel({
                    source: node,
                    datatypelookup: datatypelookup,
                    graph: self
                });
            });
            this.set('nodes', ko.observableArray(attributes.data.nodes));
            this.set('root', attributes.data.root);
            this.set('metadata', attributes.data.metadata);

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
                    ret = edge.ontologyproperty_id;
                }
            }, this);
            return ret;
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
                        self.trigger(eventname, self);
                    }
                }
            }, config));
        }

    });
});
