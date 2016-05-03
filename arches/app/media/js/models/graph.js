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

        deleteNode: function(node){
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
        },

        appendBranch: function(nodeid, property, branchmetadatid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'append_branch/' + nodeid + '/' + property + '/' + branchmetadatid,
                data: JSON.stringify(this.toJSON())
            }, function(response, status, self){
                var branchroot = response.responseJSON.root;
                response.responseJSON.nodes.forEach(function(node){
                    self.get('nodes').push(new NodeModel({
                        source: node,
                        datatypelookup: self.get('datatypelookup')
                    }));
                }, this);
                self.get('nodes')()
                .forEach(function (node) {
                    node.selected(false);
                    node.editing(false);
                    if (node.nodeid === branchroot.nodeid){
                        node.editing(true);
                        node.selected(true);
                    }
                });

                response.responseJSON.edges.forEach(function(edge){
                    self.get('edges').push(edge);
                }, this);

                callback();
            }, scope, 'changed');
        },

        moveNode: function(node, property, newParentNode, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'move_node/' + this.get('root').nodeid,
                data: JSON.stringify({nodeid:node.nodeid, property: property, newparentnodeid: newParentNode.nodeid})
            }, function(response, status, self){
                self.get('edges')()
                .find(function (edge) {
                    if(edge.edgeid === response.responseJSON.edges[0].edgeid){
                        edge.domainnode_id = response.responseJSON.edges[0].domainnode_id;
                        return true;
                    }
                    return false;
                });
                self.get('nodes')()
                .forEach(function (node) {
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

        parse: function(attributes){
            var self = this;
            var datatypelookup = {};

            attributes =_.extend({data:{'nodes':[], 'edges': []}, datatypes:[]}, attributes);

            _.each(attributes.datatypes, function(datatype){
                datatypelookup[datatype.datatype] = datatype.iconclass;
            }, this)
            this.set('datatypelookup', datatypelookup);

            attributes.data.nodes.forEach(function (node, i) {
                attributes.data.nodes[i] = new NodeModel({
                    source: node,
                    datatypelookup: datatypelookup
                });
            });
            this.set('nodes', ko.observableArray(attributes.data.nodes));
            this.set('edges', ko.observableArray(attributes.data.edges));
            this.set('root', attributes.data.root);

            this.set('editNode', ko.computed(function() {
                var editNode = _.find(self.get('nodes')(), function(node){
                    return node.editing();
                }, this);
                return editNode;
            }));

            this.set('selectedNodes', ko.computed(function() {
                var selectedNodes = _.filter(self.get('nodes')(), function(node){
                    return node.selected();
                }, this);
                return selectedNodes;
            }));
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