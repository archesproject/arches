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
        },

        appendBranch: function(nodeid, property, branchmetadatid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'append_branch/' + nodeid + '/' + property + '/' + branchmetadatid,
                data: JSON.stringify(this.toJSON())
            }, function(response, status, self){
                response.responseJSON.nodes.forEach(function(node){
                    self.get('nodes').push(new NodeModel({
                        source: node,
                        datatypelookup: self.get('datatypelookup')
                    }));
                }, this);
                self.set('_nodes', self.get('nodes')()),

                response.responseJSON.edges.forEach(function(edge){
                    self.get('edges').push(edge);
                }, this);
                self.set('_edges', self.get('edges')()),

                callback();
            }, scope, 'changed');
        },

        parse: function(attributes){
            var self = this;
            var datatypelookup = {};

            attributes =_.extend({nodes:[], edges:[], datatypes:[]}, attributes);

            _.each(attributes.datatypes, function(datatype){
                datatypelookup[datatype.datatype] = datatype.iconclass;
            }, this)
            this.set('datatypelookup', datatypelookup);

            attributes.nodes.forEach(function (node, i) {
                attributes.nodes[i] = new NodeModel({
                    source: node,
                    datatypelookup: datatypelookup
                });
            });
            this.set('nodes', ko.observableArray(attributes.nodes)),
            this.set('edges', ko.observableArray(attributes.edges)),

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