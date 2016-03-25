define([
    'backbone',
    'knockout',
    'd3'
], function(Backbone, ko, d3) {
    var GraphView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.nodes = ko.observableArray([]);
            this.edges = ko.observableArray([]);
            _.extend(this, _.pick(options, 'nodes', 'edges'));

            var diameter = this.$el.width();

            this.tree = d3.layout.tree()
                .children(function (d) {
                    var nodes = self.nodes();
                    var edges = self.edges();
                    var children = [];

                    edges.forEach(function(edge) {
                        if (edge.domainnode_id === d.nodeid) {
                            nodes.forEach(function(node) {
                                if (edge.rangenode_id === node.nodeid) {
                                    children.push(node);
                                }
                            })
                        }
                    });

                    return children;
                })
                .size([360, diameter / 2 ])
                .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

            this.diagonal = d3.svg.diagonal.radial()
                .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

            this.svg = d3.select(this.el).append("svg")
                .attr("width", "100%")
                .attr("height", $(window).height()-200)
                .call(d3.behavior.zoom().on("zoom", function() {
                    self.redraw();
                }))
                .append("g")

            this.center = [(this.$el.width() / 2) - 220, this.$el.height() / 2];
            
            this.svg.attr("transform", "translate(" + this.center[0] + "," + this.center[1] + "), rotate(0)");

            d3.select(this.el).style("height", $(window).height()-200 + "px");

            this.render();

            this.nodes.subscribe(function() {
                self.render();
            });
            this.edges.subscribe(function() {
                self.render();
            });
        },
        render: function () {
            var self = this;
            var nodesize = 6;
            var nodeMouseOver = 8;
            var root;
            this.nodes().forEach(function (node) {
                if (node.istopnode) {
                    root = node;
                }
                if (node.children) {
                    delete node.children;
                }
            });
            var nodes = this.tree.nodes(root);
            var links = this.tree.links(nodes);
            if (isNaN(nodes[0].x)) {
                nodes[0].x = 0;
            }

            var link = this.svg.selectAll(".link")
                .data(links, function(d) { return d.target.nodeid });
            link.enter().append("path")
                .attr("class", "link")
                .attr("d", this.diagonal);
            link.exit()
                .remove();

            var allNodes = this.svg.selectAll(".node")
                .data(nodes, function(d) { return d.nodeid });

            var node = allNodes.enter().append("g")
                .attr("class", "node")
                .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

            node.append("circle")
                .attr("r", nodesize)
                .on("mouseover", function() {
                    d3.select(this)
                        .attr("r", nodeMouseOver)
                        .attr("class", "nodeMouseOver")
                })
                .on("click", function (d) {
                    self.trigger('node-selected', d);
                })
                .on("mouseout", function(d) {
                    d3.select(this)
                        .attr("r", nodesize)
                        .attr("class", "node");
                });


            node.append("text")
                .attr("dy", ".31em")
                .attr("class", "node-text")
                .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
                .text(function (d) {
                    if(d.name.length > 13) {
                        return d.name.substring(0,13)+'...';
                    }
                    return d.name;
                });

            allNodes.exit()
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
    return GraphView;
});
