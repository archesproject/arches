define([
    'jquery',
    'knockout',
    'd3'
], function($, ko, d3) {
    ko.bindingHandlers.timeWheel = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var width = 750;
            var height = 600;
            var radius = Math.min(width, height) / 2;
            var colortheme = d3.scale.category20c();
            var $el = $(element);

            // Breadcrumb dimensions: width, height, spacing, width of tip/tail.
            var b = {
                w: 100,
                h: 30,
                s: 3,
                t: 10
            };

            // Mapping of step names to colors.
            var colors = {
                "HISTORIC": "#5687d1",
                "product": "#7b615c",
                "search": "#de783b",
                "account": "#6ab975",
                "other": "#a173d1",
                "end": "#bbbbbb"
            };

            // Total size of all segments; we set this later, after loading the data.
            var totalSize = 0;

            var vis = d3.select($el.find('.chart')[0]).append("svg:svg")
                .attr("width", width)
                .attr("height", height)
                .append("svg:g")
                .attr("class", "container")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            var partition = d3.layout.partition()
                .size([2 * Math.PI, radius * radius])
                .value(function(d) {
                    return d.size;
                })
                .sort(function(d) {
                    return d3.descending(d.hits);
                });

            var arc = d3.svg.arc()
                .startAngle(function(d) {
                    return d.x;
                })
                .endAngle(function(d) {
                    return d.x + d.dx;
                })
                .innerRadius(function(d) {
                    return Math.sqrt(d.y);
                })
                .outerRadius(function(d) {
                    return Math.sqrt(d.y + d.dy);
                });

            var text = 'Historic-21st Century,75,2001\nHistoric-20th Century-Late 20th Century,230,1965\nHistoric-20th Century-Middle 20th Century,190,1950\nHistoric-20th Century-WWII,207,1939\nHistoric-20th Century-Early 20th Century-WWI,377,1914\nHistoric-20th Century-Early 20th Century-Post WWI,632,1918\nHistoric-Enlightenment-1900s,1003,1900\nHistoric-Enlightenment-1800s,2108,1800\nHistoric-Enlightenment-1700s,1533,1700\nHistoric-Enlightenment-1600s,2312,1600\nHistoric-Post Midieval-Victorian,3861,1400\nHistoric-Post Midieval-Hannoverian-George I,2877,1380\nHistoric-Post Midieval-Hannoverian-George Ib,1187,1380\nHistoric-Post Midieval-Stuart-Jacobean,961,1340\nHistoric-Post Midieval-Tudor-Elizabethian,1900,1300\nHistoric-Midieval-Late Midieval,4134,1100\nHistoric-Midieval-Early Midieval,7399,900\nHistoric-Roman,18012,43\nPrehistoric-Late Prehistoric-Iron Age-Late Iron,2977,0\nPrehistoric-Late Prehistoric-Iron Age-Middle Iron,3866,-400\nPrehistoric-Late Prehistoric-Iron Age-Early Iron,5219,-800\nPrehistoric-Late Prehistoric-Bronze Age-Late Bronze,1883,-1000\nPrehistoric-Late Prehistoric-Bronze Age-Middle Bronze,2016,-1200\nPrehistoric-Late Prehistoric-Bronze Age-Early Bronze,300,-1800\nPrehistoric-Late Prehistoric-Neolithic-Late Neolithic,2196,-2000\nPrehistoric-Late Prehistoric-Neolithic-Middle Neolithic,2445,-3000\nPrehistoric-Late Prehistoric-Neolithic-Early Neolithic,988,-4500\nPrehistoric-Early Prehistoric-Mesolithic-Late Mesolithic,875,-6000\nPrehistoric-Early Prehistoric-Mesolithic-Early Mesolithic,775,-8000\nPrehistoric-Early Prehistoric-Paleolithic-Upper Paleolithic,3997,-10000\nPrehistoric-Early Prehistoric-Paleolithic-Middle Paleolithic,1009,-13000\nPrehistoric-Early Prehistoric-Paleolithic-Lower Paleolithic,8877,-15000'
            var csv = d3.csv.parseRows(text);
            var json = buildHierarchy(csv);
            createVisualization(json);

            // Main function to draw and set up the visualization, once we have the data.
            function createVisualization(json) {

                // Basic setup of page elements.
                initializeBreadcrumbTrail();


                // Bounding circle underneath the sunburst, to make it easier to detect
                // when the mouse leaves the parent g.
                vis.append("svg:circle")
                    .attr("r", radius)
                    .style("opacity", 0);

                // For efficiency, filter nodes to keep only those large enough to see.
                var nodes = partition.nodes(json)
                    .filter(function(d) {
                        return (d.dx > 0.0005); // 0.005 radians = 0.29 degrees
                    });

                var path = vis.data([json]).selectAll("path")
                    .data(nodes)
                    .enter().append("svg:path")
                    .attr("display", function(d) {
                        return d.depth ? null : "none";
                    })
                    .attr("d", arc)
                    .attr("fill-rule", "evenodd")
                    .style("fill", function(d) {
                        return colortheme((d.children ? d : d.parent).name);
                    })
                    .style("opacity", 1)
                    .on("mouseover", mouseover);

                // Add the mouseleave handler to the bounding circle.
                d3.select($el.find('.container')[0]).on("mouseleave", mouseleave);

                // Get total size of the tree = value of root node from partition.
                totalSize = path.node().__data__.value;


            };


            // Set default count value
            var percentage = "86425";
            var percentageString = percentage;

            d3.select($el.find('.percentage')[0])
                .text(percentageString);


            // Fade all but the current sequence, and show it in the breadcrumb trail.
            function mouseover(d) {

                percentage = (d.value);
                percentageString = percentage;
                if (percentage < 1) {
                    percentageString = "< 1";
                }

                d3.select($el.find('.percentage')[0])
                    .text(percentageString);

                d3.select($el.find('.explanation')[0])
                    .style("visibility", "");

                var sequenceArray = getAncestors(d);
                updateBreadcrumbs(sequenceArray, percentageString);

                // Fade all the segments.
                d3.selectAll("path")
                    .style("opacity", 0.3);

                // Then highlight only those that are an ancestor of the current segment.
                vis.selectAll("path")
                    .filter(function(node) {
                        return (sequenceArray.indexOf(node) >= 0);
                    })
                    .style("opacity", 1);
            }


            // Restore everything to full opacity when moving off the visualization.
            function mouseleave(d) {

                // Hide the breadcrumb trail
                d3.select($el.find('.trail')[0])
                    .style("visibility", "hidden");

                // Deactivate all segments during transition.
                d3.selectAll("path").on("mouseover", null);

                // Transition each segment to full opacity and then reactivate it.
                d3.selectAll("path")
                    .transition()
                    .duration(1000)
                    .style("opacity", 1)
                    .each("end", function() {
                        d3.select(this).on("mouseover", mouseover);
                    });

                d3.select($el.find('.explanation')[0])
                    .style("visibility", "hidden");
            }

            // Given a node in a partition layout, return an array of all of its ancestor
            // nodes, highest first, but excluding the root.
            function getAncestors(node) {
                var path = [];
                var current = node;
                while (current.parent) {
                    path.unshift(current);
                    current = current.parent;
                }
                return path;
            }

            function initializeBreadcrumbTrail() {
                // Add the svg area.
                var trail = d3.select($el.find('.sequence')[0]).append("svg:svg")
                    .attr("width", width)
                    .attr("height", 50)
                    .attr("class", "trail");
                // Add the label at the end, for the percentage.
                trail.append("svg:text")
                    .attr("class", "endlabel")
                    .style("fill", "#000");
            }

            // Generate a string that describes the points of a breadcrumb polygon.
            function breadcrumbPoints(d, i) {
                var points = [];
                points.push("0,0");
                points.push(b.w + ",0");
                points.push(b.w + b.t + "," + (b.h / 2));
                points.push(b.w + "," + b.h);
                points.push("0," + b.h);
                if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
                    points.push(b.t + "," + (b.h / 2));
                }
                return points.join(" ");
            }

            // Update the breadcrumb trail to show the current sequence and percentage.
            function updateBreadcrumbs(nodeArray, percentageString) {

                // Data join; key function combines name and depth (= position in sequence).
                var g = d3.select($el.find('.trail')[0])
                    .selectAll("g")
                    .data(nodeArray, function(d) {
                        return d.name + d.depth;
                    });

                // Add breadcrumb and label for entering nodes.
                var entering = g.enter().append("svg:g");

                // entering.append("svg:polygon")
                //     .attr("points", breadcrumbPoints)
                //     .style("fill", function(d) { return colors[d.name]; });

                entering.append("svg:text")
                    .attr("x", (b.w + b.t) / 2)
                    .attr("y", b.h / 2)
                    .attr("dy", "0.35em")
                    .attr("text-anchor", "middle")
                    .attr("fill", "#123")
                    .text(function(d) {
                        return d.name;
                    });

                //Set position for entering and updating nodes.
                g.attr("transform", function(d, i) {
                    return "translate(" + i * (b.w + b.s) + ", 0)";
                });

                //  var start = 0;
                //  g.attr("transform", function(d, i) {
                // start += d.name.length;
                // //console.log(start);
                //    return "translate(" + d.name.length + ", 0)";
                //  });

                // Remove exiting nodes.
                g.exit().remove();

                // Now move and update the percentage at the end.
                // d3.select("#trail").select("#endlabel")
                //     .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
                //     .attr("y", b.h / 2)
                //     .attr("dy", "0.35em")
                //     .attr("text-anchor", "middle")
                //     .text(percentageString);

                // Make the breadcrumb trail visible, if it's hidden.
                d3.select($el.find('.trail')[0])
                    .style("visibility", "");

            }




            // Take a 2-column CSV and transform it into a hierarchical structure suitable
            // for a partition layout. The first column is a sequence of step names, from
            // root to leaf, separated by hyphens. The second column is a count of how
            // often that sequence occurred.
            function buildHierarchy(csv) {
                var root = {
                    "name": "root",
                    "children": []
                };
                for (var i = 0; i < csv.length; i++) {
                    var sequence = csv[i][0];
                    var size = +csv[i][1];
                    var hits = +csv[i][2];
                    if (isNaN(size)) { // e.g. if this is a header row
                        continue;
                    }
                    var parts = sequence.split("-");
                    var currentNode = root;
                    for (var j = 0; j < parts.length; j++) {
                        var children = currentNode["children"];
                        var nodeName = parts[j];
                        var childNode;
                        if (j + 1 < parts.length) {
                            // Not yet at the end of the sequence; move down the tree.
                            var foundChild = false;
                            for (var k = 0; k < children.length; k++) {
                                if (children[k]["name"] == nodeName) {
                                    childNode = children[k];
                                    foundChild = true;
                                    break;
                                }
                            }
                            // If we don't already have a child node for this branch, create it.
                            if (!foundChild) {
                                childNode = {
                                    "name": nodeName,
                                    "children": []
                                };
                                children.push(childNode);
                            }
                            currentNode = childNode;
                        } else {
                            // Reached the end of the sequence; create a leaf node.
                            childNode = {
                                "name": nodeName,
                                "size": size,
                                "hits": hits
                            };
                            children.push(childNode);
                            // console.log(childNode);
                        }
                    }
                }
                return root;
            };

            //	Fill Colors
            var hue = d3.scale.category10();

            var luminance = d3.scale.sqrt()
                .domain([0, 1e6])
                .clamp(true)
                .range([90, 20]);

            function fill(d) {
                var p = d;
                while (p.depth > 1) p = p.parent;
                var c = d3.lab(hue(p.name));
                c.l = luminance(d.sum);
                return c;
            }

        }
    }
    return ko.bindingHandlers.timeWheel;
});
