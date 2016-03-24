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

            var diameter = 960;

            this.tree = d3.layout.tree()
                .size([360, diameter / 2 ])
                .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

            this.diagonal = d3.svg.diagonal.radial()
                .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

            this.svg = d3.select("#graph").append("svg")
                .attr("width", diameter)
                .attr("height", diameter - 150)
                .call(d3.behavior.zoom().on("zoom", function() {
                    self.redraw();
                }))
                .append("g")
                .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + "), rotate(0)");

            d3.select("#graph").style("height", diameter - 150 + "px");

            this.$el.click(function(e){
                var x = e.pageX + 15;
                var y = e.pageY;

                var xScreen = e.clientX;
                var yScreen = e.clientY;
                var windowHeight = $(window).height();
            });

            this.render();
        },
        render: function () {
            var nodesize = 6;  //Default node size
            var nodeMouseOver = 8;
            var nodes = this.tree(this.nodes());
            var links = this.edges();

            var link = this.svg.selectAll(".link")
                .data(links)
                .enter().append("path")
                .attr("class", "link")
                .attr("d", this.diagonal);

            var node = this.svg.selectAll(".node")
                .data(nodes)
                .enter().append("g")
                .attr("class", "node")
                // .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })


            node.append("circle")
                .attr("r", nodesize)
                .on("mouseover", function() {
                    d3.select(this)
                    .attr("r", nodeMouseOver)
                    .attr("class", "nodeMouseOver")
                })
                .on("click", function (d) {
                    d3.select(this)

                    var nodeName = d.entitytypeid;

                    d3.select("#nodeCrud")
                    .select("#nodeName")
                    .text(nodeName);
                })
                .on("mouseout", function(d) {
                    d3.select(this)
                    .attr("r", nodesize)
                    .attr("class", "node");
                });


            node.append("text")
                .attr("dy", ".31em")
                .attr("class", "node-text")
                // .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                // .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
                .text(function (d) {
                    // if(d.entitytypeid.length > 13)
                    // return d.entitytypeid.substring(0,13)+'...';
                    // else
                    // return d.entitytypeid;
                    console.log(d);
                    return d.name;
                });

        },
        redraw: function () {
            var xt = d3.event.translate[0] + 180;

            this.svg.attr("transform",
                "translate(" + xt + "," + d3.event.translate[1] + ")" +
                " scale(" + d3.event.scale + ")");
        }
    });
    return GraphView;
});
