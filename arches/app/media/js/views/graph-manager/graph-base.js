define([
    'backbone',
    'knockout',
    'd3'
], function(Backbone, ko, d3) {
    var GraphBase = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.nodes = ko.observableArray([]);
            this.edges = ko.observableArray([]);
            _.extend(this, _.pick(options, 'nodes', 'edges'));

            var diameter = this.$el.width();

            this.tree = d3.layout.tree()
                .children(function (d) {
                    var nodes = self.nodes();
                    return self.edges()
                        .filter(function (edge) {
                            return edge.domainnode_id === d.nodeid;
                        })
                        .map(function (edge) {
                            return nodes.find(function (node) {
                                return edge.rangenode_id === node.nodeid;
                            });
                        });
                })
                .size([360, diameter / 2 ])
                .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

            this.diagonal = d3.svg.diagonal.radial()
                .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

            this.svg = d3.select(this.el).append("svg")
                .attr("width", "100%")
                .attr("height", this.$el.height())
                .call(d3.behavior.zoom().on("zoom", function() {
                    self.redraw();
                }))
                .append("g")

            this.center = [(this.$el.width() / 2), this.$el.height() / 2];

            this.svg.attr("transform", "translate(" + this.center[0] + "," + this.center[1] + "), rotate(0)");

            d3.select(this.el).style("height", this.$el.height() + "px");

            this.render();
        },
        render: function () {
            var self = this;
            this.root = undefined;
            this.nodesize = 6;
            this.nodes().forEach(function (node) {
                if (node.istopnode) {
                    this.root = node;
                }
                if (node.children) {
                    delete node.children;
                }
            }, this);

            this.renderLinks();

            var nodes = this.tree.nodes(this.root);
            if (isNaN(nodes[0].x)) {
                nodes[0].x = 0;
            }
            this.allNodes = this.svg.selectAll(".node")
                .data(nodes, function(d) { return d.nodeid });

            this.node = this.allNodes.enter().append("g")
                .attr("class", 'node')
                .attr("transform", function(d) { 
                    return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; 
                });

            this.renderNodes();
            this.renderNodeText();
        },
        renderNodes: function(){
            this.node.append("circle")
                .attr("r", this.nodesize)

        },
        renderNodeText: function(){
            this.node.append("text")
                .attr("dy", ".31em")
                .attr("class", "node-text")
                .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; });

            this.allNodes.selectAll('text')
                .text(function (d) {
                    if(d.name().length > 13) {
                        return d.name().substring(0,13)+'...';
                    }
                    return d.name();
                });
        },
        renderLinks: function(){
            var nodes = this.tree.nodes(this.root);
            var links = this.tree.links(nodes);

            var link = this.svg.selectAll(".link")
                .data(links, function(d) { return d.target.nodeid });
            link.enter().append("path")
                .attr("class", "link")
                .attr("d", this.diagonal);
            link.exit()
                .remove();
        },
        redraw: function () {
            var xt = d3.event.translate[0] + this.center[0];
            var yt = d3.event.translate[1] + this.center[1];

            this.svg.attr("transform",
                "translate(" + xt + "," + yt + ")" +
                " scale(" + d3.event.scale + ")");
        }
    });
    return GraphBase;
});
