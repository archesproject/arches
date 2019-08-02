define([
    'backbone',
    'knockout',
    'd3'
], function(Backbone, ko, d3) {
    var GraphBase = Backbone.View.extend({
        /**
        * A backbone view to for rendering D3 graphs comprised of nodes and edges as svg
        * @augments Backbone.View
        * @constructor
        * @name GraphBase
        */

        /**
        * Initializes the view with optional parameters
        * @memberof GraphBase.prototype
        * @param {object} options
        * @param {object} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            var self = this;
            options = _.defaults(options, {nodeSize: 11, labelOffset: 2, loading: ko.observable(false)});
            this.loading = options.loading;
            this.nodeSize = options.nodeSize;
            this.labelOffset = options.labelOffset;
            this.nodeLabelOffset = this.nodeSize + this.labelOffset;
            this.currentOffset = [0,0];
            this.currentScale = 1;
            this.graphModel = options.graphModel;
            this.nodes = options.graphModel.get('nodes') || ko.observableArray([]);
            this.edges = options.graphModel.get('edges') || ko.observableArray([]);
            this.getsize = function(){
                return 1000;
                // console.log((this.nodes().length * 5) + 500)
                // return (this.nodes().length * 30) + 500;
            };

            var diameter = this.$el.width() < this.$el.height() ? this.$el.width() : this.$el.height();

            this.tree = d3.layout.tree()
                .children(function (d) {
                    return d.childNodes();
                })
                .size([360, this.getsize()])
                .separation(function(a, b) {
                    return (a.parent == b.parent ? 1 : 2) / a.depth;
                });

            this.diagonal = d3.svg.diagonal.radial()
                .projection(function(d) {
                    return [d.y, d.x / 180 * Math.PI];
                });

            this.zoom = d3.behavior.zoom().on("zoom", function() {
                    self.redraw();
                });

            this.svg = d3.select(this.el).append("svg")
                .attr("width", "100%")
                .attr("height", this.$el.height())
                .call(this.zoom)
                .append("g")

            this.render();
            setTimeout(function(){
                self.resize();
            }, 50);
        },

        /**
        * Renders the nodes and edges as a D3 graph
        * @memberof GraphBase.prototype
        */
        render: function () {
            var self = this;
            this.root = undefined;

            this.nodes().forEach(function (node) {
                if (node.istopnode) {
                    this.root = node;
                }
            }, this);

            this.tree_nodes = this.tree.nodes(this.root);
            this.tree_nodes.forEach(function(node){
                if (isNaN(node.x)) {
                    node.x = 0;
                }
            })

            this.renderLinks();
            this.renderNodes();
        },

        /**
        * Renders only the nodes in the graph
        * @memberof GraphBase.prototype
        */
        renderNodes: function(){
            this.allNodes = this.svg.selectAll("g")
                .data(this.tree_nodes, function(d) { return d.nodeid });

            this.node = this.allNodes.enter().append("g")
                .attr("class", 'node')
                .attr("transform", function(d) {
                    return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
                });

            this.node.append("circle")
                .attr("r", this.nodeSize)

            this.renderNodeText();
        },

        /**
        * Renders the text associated with each node in the graph
        * @memberof GraphBase.prototype
        */
        renderNodeText: function(){
            var self = this;
            this.node.append("text")
                .attr("dy", function(d){return d.children ? "-.31em" : ".31em"})
                .attr("class", 'graph-node-text')
                .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                .attr("transform", function(d) { return d.x < 180 ? "translate(" + self.nodeLabelOffset + ")" : "rotate(180)translate(-" + self.nodeLabelOffset + ")"; })
                .text(function (d) {
                    if(d.name().length > 16*self.currentScale) {
                        return d.name().substring(0,16*self.currentScale)+'...';
                    }
                    return d.name();
                });
        },

        /**
        * Renders only the edges in the graph
        * @memberof GraphBase.prototype
        */
        renderLinks: function(){
            var links = this.tree.links(this.tree_nodes);

            var link = this.svg.selectAll(".link")
                .data(links, function(d) { return d.target.nodeid });
            link.enter().append("path")
                .attr("class", "link")
                .attr("d", this.diagonal);
            link.exit()
                .remove();
        },

        /**
        * Redraw the graph based on the current D3 scale and translate events
        * @memberof GraphBase.prototype
        * @param {boolean} [force=false] - if true remove and re-add all the nodes and edges in the graph,
        * used after adding/removing nodes from the graph
        */
        redraw: function (force) {
            var self = this;
            var previousScale = this.currentScale;
            force = force || false;

            if (d3.event){
                this.currentScale = d3.event.scale || this.currentScale;
                this.currentOffset = d3.event.translate || this.currentOffset;
            }

            if (!(this.center)){
                this.center = [(this.$el.width() / 2), this.$el.height() / 2];
            }

            var xt = this.currentOffset[0] + this.center[0];
            var yt = this.currentOffset[1] + this.center[1];

            this.svg.attr("transform",
                "translate(" + xt + "," + yt + ")" +
                " scale(" + this.currentScale + ")");

            if (force || previousScale !== this.currentScale){
                this.allNodes.remove();
                this.svg.selectAll(".link").remove();
                this.tree = d3.layout.tree()
                    .children(function (d) {
                        return d.childNodes();
                    })
                    .size([360, this.getsize() * this.currentScale])
                    .separation(function(a, b) {
                        return (a.parent == b.parent ? 1 : 2) / (a.depth);
                    });
                this.render();
            }
        },

        /**
        * Resizes the rendered svg graph to fit it's enclosing html container
        * @memberof GraphBase.prototype
        */
        resize: function(){
            d3.select(this.el)
                .style("height", this.$el.height() + "px")
                .select("svg")
                    .attr("height", this.$el.height());

            this.center = [(this.$el.width() / 2), this.$el.height() / 2];
            var xt = this.currentOffset[0] + this.center[0];
            var yt = this.currentOffset[1] + this.center[1];

            this.svg.attr("transform",
                "translate(" + xt + "," + yt + ")" +
                " scale(" + this.currentScale + ")");
        },

        zoomTo: function (node) {
            var x = -node.y * Math.cos((node.x - 90) / 180 * Math.PI)*this.currentScale;
            var y = -node.y * Math.sin((node.x - 90) / 180 * Math.PI)*this.currentScale;

            var trans = this.zoom
                .translate([x, y]);
            this.svg.transition()
                .duration(1000)
                .call(trans.event);
        }
    });
    return GraphBase;
});
