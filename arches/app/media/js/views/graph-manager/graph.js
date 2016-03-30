define([
    'backbone',
    'views/graph-manager/graph-base',
    'knockout',
    'd3'
], function(Backbone, GraphBase, ko, d3) {
    var GraphView = GraphBase.extend({
        initialize: function(options) {
            GraphBase.prototype.initialize.apply(this, arguments);

            this.addNodeListeners();
            this.nodes.subscribe(function() {
                this.render();
                this.addNodeListeners();
            }, this);
            this.edges.subscribe(function() {
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
        addNodeListeners: function () {
            var self = this;
            var nodes = this.nodes();

            nodes.forEach(function (node) {
                node.name.subscribe(function () {
                    self.render();
                });
            });
        },
        redraw: function () {
            var xt = d3.event.translate[0] + this.center[0];
            var yt = d3.event.translate[1] + this.center[1];

            this.svg.attr("transform",
                "translate(" + xt + "," + yt + ")" +
                " scale(" + d3.event.scale + ")");
        }
    });
    return GraphView;
});
