define(['jquery', 'backbone', 'd3'], function($, Backbone) {
    return Backbone.View.extend({

        initialize: function() {
            var self = this,
                width = self.$el.parent().width() - 20, //A hack to get a dynamic width because the #svg doesn't exist until the user opens it
                svgDiv = this.$el.find(".svg")[0],
                height = $(svgDiv).height(),

                force = d3.layout.force()
                    .charge(-1550)
                    .linkDistance(90)
                    .gravity(0.05)
                    .friction(0.55)
                    .linkStrength(function(l, i) {
                        return 1;
                    })
                    .theta(0.8)
                    .size([width, height]),

                svg = d3.select(svgDiv).append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .call(d3.behavior.zoom().on("zoom", function() {
                        svg.attr("transform",
                            "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
                    }))
                    .append('svg:g'),

                data = JSON.parse(this.$el.find('.graph_json_content').html()),
                n = data.nodes.length,
                canvasd3 = $(svgDiv),
                aspect = canvasd3.width() / canvasd3.height(),
                containerd3 = canvasd3.parent(),
                drag = force.drag()
                    .on("dragstart", self.dragstart),

                link = svg.selectAll(".link")
                    .data(data.links)
                    .enter().append("line")
                    .attr("class", "link")
                    .attr("marker-end", "url(#arrowGray)")
                    //add interactivity
                    .on("mouseover", function(d) {
                        d3.select(this)
                            .attr("class", "linkMouseover");

                        //add tooltup to show edge property
                        link.append("title")
                            .text(function(d) {
                                return d.relationship;
                            });
                    })
                    .on("mouseout", function(d) {
                        d3.select(this)
                            .attr("class", "link");
                    }),

                defs = svg.append('defs'),
                node = svg.selectAll(".node").data(data.nodes)
                    .enter().append("circle")
                    .attr("r", function(d) {
                        if (d.type == "Current") {
                            return 30;
                        } else if (d.type == "Ancestor" || d.type == "Root") {
                            return 22;
                        } else {
                            return 16;
                        }
                    })
                    //.attr("class", "node")
                    .attr("class", function(d) {
                        if (d.type == "Current") {
                            return "node-current";
                        } else if (d.type == "Ancestor" || d.type == "Root") {
                            return "node-ancestor";
                        } else {
                            return "node-descendent";
                        }
                    })
                    .on("mouseover", function() {
                        d3.select(this).attr("class", function(d) {
                            if (d.type == "Current") {
                                return "node-current-over";
                            } else if (d.type == "Ancestor") {
                                return "node-ancestor-over";
                            } else {
                                return "node-descendent-over";
                            }
                        });
                    })
                    .on("mouseout", function() {
                        d3.select(this).attr("class", function(d) {
                            //Update node class
                            if (d.type == "Current") {
                                return "node-current";
                            } else if (d.type == "Ancestor") {
                                return "node-ancestor";
                            } else {
                                return "node-descendent";
                            }
                        });
                    })
                    .on("click", function(d) {
                        //Get the Node Name
                        var nodeName = d.name;

                        d3.select(self.$el.find('.node_info')[0])
                            .select(".concept-label")
                            .text(nodeName);
                        $('.concept-label').data('conceptid', d.concept_id);

                        $('.graph-concept-delete-link').hide();
                        if (d.type === "Descendant") {
                            $('.graph-concept-delete-link').data('id', d.concept_id);
                            $('.graph-concept-delete-link').show();
                        }

                        //Show the form
                        d3.select(self.$el.find('.node_info')[0]).classed("hidden", false);

                        //Highlight the selected node.  Start by clearing the "node-selected" class from any previously clicked node
                        d3.selectAll("circle").classed("node-selected", false);


                        //Append the "node-selected" class to the clicked node
                        if (d3.select(this).classed("node-ancestor-over")) {
                            d3.select(this).attr("class", "node-ancestor node-selected");
                        } else if (d3.select(this).classed("node-descendent-over")) {
                            d3.select(this).attr("class", "node-descendent node-selected");
                        } else if (d3.select(this).classed("node-current-over")) {
                            d3.select(this).attr("class", "node-current node-selected");
                        }
                    })
                    .on("dblclick", self.dblclick)
                    .call(drag),

                texts = svg.selectAll("text.nodeLabels")
                    .data(data.nodes)
                    .enter().append("text")
                    .attr("class", function(d) {
                        if (d.type == "Current") {
                            return "node-current-label";
                        } else if (d.type == "Ancestor" || d.type == "Root") {
                            return "node-ancestor-label";
                        } else {
                            return "node-descendent-label";
                        }
                    })
                    .attr("dy", ".35em")
                    .text(function(d) {
                        return d.name;
                    }),

                labels = svg.selectAll('text.edgeLabels')
                    .data(data.links)
                    .enter().append('text')
                    .attr('class', 'edgeLabels');

            data.nodes.forEach(function(d, i) {
                if (d.type === 'Current') {
                    d.fixed = true;
                    d.x = width * 0.55;
                    d.y = height * 0.55;
                }
                if (d.type === 'Root') {
                    d.fixed = true;
                    d.x = width * 0.1;
                    d.y = height * 0.1;
                }
            });

            //Manage D3 graph on resize of window
            $(window).on("resize", function() {
                var targetWidth = containerd3.width();
                var targetHeight = containerd3.height();
                canvasd3.attr("width", targetWidth);
                canvasd3.attr("height", targetHeight);

                //Start the simulation
                force.nodes(data.nodes)
                    .links(data.links)
                    .start();
            }).trigger("resize");

            defs.append("svg:marker")
                .attr("id", "arrowGray")
                .attr("viewBox", "0 0 10 10")
                .attr("refX", "28")
                .attr("refY", "5")
                .attr("markerUnits", "strokeWidth")
                .attr("markerWidth", "5")
                .attr("markerHeight", "2")
                .attr("orient", "auto")
                .append("svg:path")
                .attr("d", "M 0 0 L 10 5 L 0 10 z")
                .attr("fill", "#BBBBBB");

            force.on("tick", function(e) {
                //Push nodes toward their designated focus.
                var k = 0.1 * e.alpha,
                    foci = {
                        "Root": {
                            x: 0,
                            y: 0
                        }, // set to fixed above
                        "Ancestor": {
                            x: width * 0.1,
                            y: height * 0.1
                        },
                        "Current": {
                            x: 150,
                            y: 250
                        }, // set to fixed above
                        "Descendant": {
                            x: width * 0.55,
                            y: height * 1.4
                        }
                    };

                data.nodes.forEach(function(o, i) {
                    o.y += (foci[o.type].y - o.y) * k;
                    o.x += (foci[o.type].x - o.x) * k;
                });

                link.attr("x1", function(d) {
                        return d.source.x;
                    })
                    .attr("y1", function(d) {
                        return d.source.y;
                    })
                    .attr("x2", function(d) {
                        return d.target.x;
                    })
                    .attr("y2", function(d) {
                        return d.target.y;
                    });

                node.attr("cx", function(d) {
                        return d.x;
                    })
                    .attr("cy", function(d) {
                        return d.y;
                    });

                texts.attr("x", function(d) {
                        return d.x;
                    })
                    .attr("y", function(d) {
                        return d.y;
                    });

                labels.attr("x", function(d) {
                        return (d.source.x + d.target.x) / 2;
                    })
                    .attr("y", function(d) {
                        return (d.source.y + d.target.y) / 2;
                    });
            });

        },
        dblclick: function(d) {
            d3.select(this).classed("fixed", d.fixed = false);
        },
        dragstart: function(d) {
            d3.select(this).classed("fixed", d.fixed = true);
        }
    });
});