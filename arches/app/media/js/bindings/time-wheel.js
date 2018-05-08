define([
    'jquery',
    'underscore',
    'knockout',
    'd3'
], function($, _, ko, d3) {
    ko.bindingHandlers.timeWheel = {

        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var width = 750;
            var height = 600;
            var radius = Math.min(width, height) / 2;
            var $el = $(element);

            var vis = d3.select($el.find('.chart')[0]).append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("class", "container")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            vis.append("svg:circle")
                .attr("r", radius)
                .style("opacity", 0);

            ko.utils.domData.set(element, 'vis', vis);
        },

        update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var width = 750;
            var height = 600;
            var radius = Math.min(width, height) / 2;
            var colortheme = d3.scale.category20c();
            var x = d3.scale.linear()
                .range([0, 2 * Math.PI]);
            var y = d3.scale.sqrt()
                .range([0, radius]);
            var $el = $(element);
            var opts = ko.unwrap(valueAccessor());
            var configJSON = opts.config();
            var breadCrumb = opts.breadCrumb;
            var selectedPeriod = opts.selectedPeriod;
            var total = 0;
            var data = null;

            // Breadcrumb dimensions: width, height, spacing, width of tip/tail.
            var b = {
                w: 100,
                h: 30,
                s: 3,
                t: 10
            };

            var vis = ko.utils.domData.get(element, 'vis');
            vis.on("mouseleave", function () {
                var d = selectedPeriod();
                if (d) {
                    highlightPeriod(d);
                } else {
                    clearHighlight();
                }
            });

            var partition = d3.layout.partition()
                .sort(function(d, e) {
                    return d.start - e.start;
                })
                .value(function(d) {
                    return d.size;
                });

            if (configJSON) {
                data = partition.nodes(configJSON);
                total = _.find(data, function(d) {
                    return d.name === 'root';
                }).value;
                breadCrumb(total + ' date values');
            }

            var arc = d3.svg.arc()
                .startAngle(function(d) {
                    return Math.max(0, Math.min(2 * Math.PI, x(d.x)));
                })
                .endAngle(function(d) {
                    return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx)));
                })
                .innerRadius(function(d) {
                    return Math.max(0, y(d.y));
                })
                .outerRadius(function(d) {
                    return Math.max(0, y(d.y + d.dy));
                });


            var arcTween = function(d) {
                var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
                    yd = d3.interpolate(y.domain(), [d.y, 1]),
                    yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
                return function(d, i) {
                    return i ?
                        function(t) {
                            return arc(d);
                        } :
                        function(t) {
                            x.domain(xd(t));
                            y.domain(yd(t)).range(yr(t));
                            return arc(d);
                        };
                };
            };

            function clickcancel() {
                // we want to a distinguish single/double click
                // details http://bl.ocks.org/couchand/6394506
                var event = d3.dispatch('click', 'dblclick');
                function cc(selection) {
                    var down, tolerance = 5, last, wait = null, args;
                    // euclidean distance
                    function dist(a, b) {
                        return Math.sqrt(Math.pow(a[0] - b[0], 2), Math.pow(a[1] - b[1], 2));
                    }
                    selection.on('mousedown', function() {
                        down = d3.mouse(document.body);
                        last = +new Date();
                        args = arguments;
                    });
                    selection.on('mouseup', function() {
                        if (dist(down, d3.mouse(document.body)) > tolerance) {
                            return;
                        } else {
                            if (wait) {
                                window.clearTimeout(wait);
                                wait = null;
                                event.dblclick.apply(this, args);
                            } else {
                                wait = window.setTimeout((function() {
                                    return function() {
                                        event.click.apply(this, args);
                                        wait = null;
                                    };
                                })(), 300);
                            }
                        }
                    });
                };
                return d3.rebind(cc, event, 'on');
            }
            var cc = clickcancel();

            var updateChart = function (data) {
                // DATA JOIN - Join new data with old elements, if any.
                var gs = vis.selectAll("g").data(data);

                // ENTER
                var g = gs.enter()
                    .append("g")
                    .on("mouseover", highlightPeriod)
                    .call(cc);

                // click and dblclick step on each other so we need this
                cc.on("click", function(d) {
                    selectedPeriod(d);
                })
                .on("dblclick", dblclick)

                // UPDATE
                var path = g.append("path");

                gs.select('path')
                    .style("fill", function(d) {
                        return colortheme((d.children ? d : d.parent).name);
                    })
                    .each(function(d) {
                      this.x0 = d.x;
                      this.dx0 = d.dx;
                    })
                    .transition().duration(500)
                    .attr("d", arc);


                // EXIT - Remove old elements as needed.
                gs.exit().transition().duration(500).style("fill-opacity", 1e-6).remove();

            }

            function dblclick(d) {
                // console.log(d)
                // fade out all text elements
                if (d.size !== undefined) {
                  d.size += 100;
                };

                vis.selectAll('path').transition()
                  .duration(750)
                  .attrTween("d", arcTween(d))
                  .each("end", function(e, i) {
                      // check if the animated element's data e lies within the visible angle span given in d
                      if (e.x >= d.x && e.x < (d.x + d.dx)) {
                          // get a selection of the associated text element
                          var arcText = d3.select(this.parentNode).select("text");
                          // fade in the text element and recalculate positions
                          arcText.transition().duration(750)
                              .attr("opacity", 1)
                              .attr("transform", function() {
                                  return "rotate(" + computeTextRotation(e) + ")"
                              })
                              .attr("x", function(d) {
                                  return y(d.y);
                              });
                      }
                });
            }

            function highlightPeriod(d) {
                count = d.size;
                if (d.size < 1) {
                    count = "< 1";
                }

                d3.select($el.find('.count')[0])
                    .text(count);

                var sequenceArray = [];
                var current = d;
                while (current.parent) {
                    sequenceArray.unshift(current.name);
                    current = current.parent;
                }

                sequenceArray.push(count + ' hits')

                breadCrumb(sequenceArray.join(' - '));

                // Fade all the segments.
                d3.selectAll("path")
                    .style("opacity", 0.3);

                // Then highlight only those that are an ancestor of the current segment.
                vis.selectAll("path")
                    .filter(function(node) {
                        return (sequenceArray.indexOf(node.name) >= 0);
                    })
                    .style("opacity", 1);
            }

            function clearHighlight(){
                // Deactivate all segments during transition.
                d3.selectAll("path").on("mouseover", null);

                // Transition each segment to full opacity and then reactivate it.
                d3.selectAll("path")
                    .transition()
                    .duration(1000)
                    .style("opacity", 1)
                    .each("end", function() {
                        d3.select(this).on("mouseover", highlightPeriod);
                    });

                breadCrumb(total + ' date values')
            }

            selectedPeriod.subscribe(function(d) {
                if (!d) {
                    clearHighlight();
                }
            })

            if(data){
                updateChart(data);
            }

        }
    }
    return ko.bindingHandlers.timeWheel;
});
