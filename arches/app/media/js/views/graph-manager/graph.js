define([
    'backbone',
    'views/graph-manager/graph-base',
    'knockout',
    'd3'
], function(Backbone, GraphBase, ko, d3) {
    var GraphView = GraphBase.extend({
        initialize: function(options) {
            this.editNode = options.graphModel.get('editNode');
            this.selectedNodes = options.graphModel.get('selectedNodes');
            GraphBase.prototype.initialize.apply(this, arguments);

            this.addNodeListeners();
            this.nodes.subscribe(function() {
                this.render();
                this.addNodeListeners();
            }, this);
            this.edges.subscribe(function() {
                this.render();
            }, this);

            ko.computed(function() {
                this.editNode();
                this.selectedNodes();
                this.render();
            }, this);
        },
        renderNodes: function(){
            GraphBase.prototype.renderNodes.apply(this, arguments);
            var self = this;
            var nodeMouseOver = 8;
            var getNodeClass = function (d, className) {
                className += d.editing() ? ' node-editing' : '';
                className += d.selected() ? ' node-selected' : '';
                className += (self.editNode() && self.editNode().nodeGroupId() === d.nodeGroupId()) ? ' node-collected' : '';
                return className;
            }
            this.allNodes.selectAll('circle')
                .attr("class", function (d) {
                    return getNodeClass(d, '');
                })
                .on("mouseover", function() {
                    d3.select(this)
                        .attr("r", nodeMouseOver)
                        .attr("class", function (d) {
                            return getNodeClass(d, 'node-over');
                        })
                })
                .on("click", function (node) {
                    self.trigger('node-clicked', node);
                })
                .on("mouseout", function(d) {
                    d3.select(this)
                        .attr("r", self.nodesize)
                        .attr("class", function (d) {
                            return getNodeClass(d, '');
                        });
                });

            this.allNodes.exit()
                .remove();
        },
        renderLinks: function(){
            var self = this;
            GraphBase.prototype.renderLinks.apply(this, arguments);
            this.svg.selectAll(".link")
                .attr("class", function (d) {
                    var className = 'link';
                    if (self.editNode()) {
                        var selectedGroup = self.editNode().nodeGroupId();
                        if (d.source.nodeGroupId() === selectedGroup && d.target.nodeGroupId() === selectedGroup) {
                            className += ' link-collected';
                        }
                    }
                    return className;
                });
        },
        addNodeListeners: function () {
            var self = this;
            var nodes = this.nodes();

            nodes.forEach(function (node) {
                node.name.subscribe(function () {
                    self.render();
                });
                node.nodeGroupId.subscribe(function () {
                    self.render();
                });
            });
        }
    });
    return GraphView;
});
