define([
    'jquery',
    'underscore',
    'knockout',
    'd3'
], function($, _, ko, d3) {
    var width = 300;
    var height = 300;
    var radius = Math.min(width, height) / 8;
    ko.bindingHandlers.timeWheel = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var $el = $(element);

            var g = d3.select($el.find('.chart')[0]).append("svg")
                .attr("preserveAspectRatio", "xMinYMin meet")
                .attr("viewBox", [0, 0, width ,height])
                .classed("svg-content", true)
                .append("g")
                .attr("class", "container")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            // g.append("svg:circle")
            //     .attr("r", "0")
            //     .style("opacity", 0);

            ko.utils.domData.set(element, 'vis', g);
        },

        update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            // see https://observablehq.com/@d3/zoomable-sunburst for the example that informed much of this code
            // also see http://bl.ocks.org/ropeladder/83915942ac42f17c087a82001418f2ee for the click/dblclick code

            var colortheme = d3.scaleOrdinal(d3.schemeCategory10);
            var x = d3.scaleLinear()
                .range([0, 2 * Math.PI]);
            var y = d3.scaleSqrt()
                .range([0, radius]);
            var $el = $(element);
            var opts = ko.unwrap(valueAccessor());
            var configJSON = opts.config();
            var breadCrumb = opts.breadCrumb;
            var selectedPeriod = opts.selectedPeriod;
            var total = 0;
            var data = null;
            var depth = 0;

            // Breadcrumb dimensions: width, height, spacing, width of tip/tail.
            var b = {
                w: 100,
                h: 30,
                s: 3,
                t: 10
            };

            selectedPeriod.subscribe(function(d) {
                if (!d) {
                    clearHighlight();
                }
            })

            var g = ko.utils.domData.get(element, 'vis');
            g.on("mouseleave", function () {
                var d = selectedPeriod();
                if (d) {
                    highlightPeriod(d);
                } else {
                    clearHighlight();
                }
            });

            var partition = function(data) {
                var root = d3.hierarchy(data)
                    .sort(function(d, e) {
                        return d.start - e.start;
                    })
                    .sum( function(d) { 
                        // we only want leaf nodes to specify a size
                        // otherwise the sunburst chart will be sparcely populated
                        return d.children.length > 0 ? 0 : d.size;
                    });
                depth = root.height + 1;
                return d3.partition()
                    .size([2 * Math.PI, root.height + 1])
                    (root);
            }

            // // var partition = d3.partition()
            // //     // .sort(function(d, e) {
            // //     //     return d.start - e.start;
            // //     // })
            // //     .value(function(d) {
            // //         return d.size;
            // //     });

            // var arc = d3.arc()
            //     .startAngle(d => d.x0)
            //     .endAngle(d => d.x1)
            //     .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
            //     .padRadius(radius * 1.5)
            //     .innerRadius(d => d.y0 * radius)
            //     .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

            // // var arc = d3.arc()
            // //     .startAngle(function(d) {
            // //         return Math.max(0, Math.min(2 * Math.PI, x(d.x)));
            // //     })
            // //     .endAngle(function(d) {
            // //         return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx)));
            // //     })
            // //     .innerRadius(function(d) {
            // //         return Math.max(0, y(d.y));
            // //     })
            // //     .outerRadius(function(d) {
            // //         return Math.max(0, y(d.y + d.dy));
            // //     });


            // var arcTween = function(d) {
            //     var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
            //         yd = d3.interpolate(y.domain(), [d.y, 1]),
            //         yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
            //     return function(d, i) {
            //         return i ?
            //             function(t) {
            //                 return arc(d);
            //             } :
            //             function(t) {
            //                 x.domain(xd(t));
            //                 y.domain(yd(t)).range(yr(t));
            //                 return arc(d);
            //             };
            //     };
            // };

            function d3ClickManager() {
                // we want to a distinguish single/double click
                // details http://bl.ocks.org/couchand/6394506
                var dispatcher = d3.dispatch('click', 'dblclick');
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
                                dispatcher.apply("dblclick", this, args);
                            } else {
                                wait = window.setTimeout((function() {
                                    return function() {
                                        dispatcher.apply("click", this, args);
                                        wait = null;
                                    };
                                })(), 300);
                            }
                        }
                    });
                };
                // Copies a variable number of methods from source to target.
                var d3rebind = function(target, source) {
                    var i = 1, n = arguments.length, method;
                    while (++i < n) target[method = arguments[i]] = d3_rebind(target, source, source[method]);
                    return target;
                };

                // Method is assumed to be a standard D3 getter-setter:
                // If passed with no arguments, gets the value.
                // If passed with arguments, sets the value and returns the target.
                function d3_rebind(target, source, method) {
                    return function() {
                    var value = method.apply(source, arguments);
                    return value === source ? target : value;
                    };
                }
                return d3rebind(cc, dispatcher, 'on');
            }
            var clickmanager = d3ClickManager();
            clickmanager.on("click", function(d) {
                selectedPeriod(d);
            })
            .on("dblclick", function(d) {
                dblclick(d);
            });

            //     function rebind(target, source) {
            //         var i = 1,
            //             n = arguments.length,
            //             method;
            //         while (++i < n) target[method = arguments[i]] = d3_rebind(target, source, source[method]);
            //         return target;
            //     };

            //     function d3_rebind(target, source, method) {
            //         return function() {
            //             var value = method.apply(source, arguments);
            //             return value === source ? target : value;
            //         };
            //     }
            //     return rebind(cc, event, 'on');

            // }
            // var cc = d3ClickManager();

            // var updateChart = function (data) {

            //     // DATA JOIN - Join new data with old elements, if any.
            //     var gs = vis.selectAll("g").data(data);

            //     // ENTER
            //     var g = gs.enter()
            //         .append("g")
            //         .on("mouseover", highlightPeriod)
            //         .call(cc);

            //     // click and dblclick step on each other so we need this
            //     cc.on("click", function(d) {
            //         selectedPeriod(d);
            //     })
            //     .on("dblclick", dblclick)

            //     // UPDATE
            //     var path = g.append("path");

            //     gs.select('path')
            //         .style("fill", function(d) {
            //             return colortheme((d.children ? d : d.parent).name);
            //         })
            //         .each(function(d) {
            //           this.x0 = d.x;
            //           this.dx0 = d.dx;
            //         })
            //         .transition().duration(500)
            //         .attr("d", arc);


            //     // EXIT - Remove old elements as needed.
            //     gs.exit().transition().duration(500).style("fill-opacity", 1e-6).remove();

            // }

            // function dblclick(d) {
            //     // console.log(d)
            //     // fade out all text elements
            //     if (d.size !== undefined) {
            //       d.size += 100;
            //     };

            //     vis.selectAll('path').transition()
            //       .duration(750)
            //       .attrTween("d", arcTween(d))
            //       .each("end", function(e, i) {
            //           // check if the animated element's data e lies within the visible angle span given in d
            //           if (e.x >= d.x && e.x < (d.x + d.dx)) {
            //               // get a selection of the associated text element
            //               var arcText = d3.select(this.parentNode).select("text");
            //               // fade in the text element and recalculate positions
            //               arcText.transition().duration(750)
            //                   .attr("opacity", 1)
            //                   .attr("transform", function() {
            //                       return "rotate(" + computeTextRotation(e) + ")"
            //                   })
            //                   .attr("x", function(d) {
            //                       return y(d.y);
            //                   });
            //           }
            //     });
            // }

            function highlightPeriod(d) {
                count = d.data.size;
                if (d.data.size < 1) {
                    count = "< 1";
                }

                d3.select($el.find('.count')[0])
                    .text(count);

                var sequenceArray = [];
                var current = d;
                while (current.parent) {
                    sequenceArray.unshift(current.data.name);
                    current = current.parent;
                }

                sequenceArray.push(count + ' hits')

                breadCrumb(sequenceArray.join(' - '));

                // Fade all the segments.
                d3.selectAll("path")
                    .style("opacity", 0.3);

                // Then highlight only those that are an ancestor of the current segment.
                path.filter(function(d) {
                    return (sequenceArray.indexOf(d.data.name) >= 0);
                })
                .style("opacity", 1);
            }

            function clearHighlight(){
                // Deactivate all segments during transition.
                // d3.selectAll("path").on("mouseover", null);

                // Transition each segment to full opacity and then reactivate it.
                d3.selectAll("path")
                    //.transition()
                    //.duration(1000)
                    .style("opacity", 1)
                    // .each("end", function() {
                    //     d3.select(this).on("mouseover", highlightPeriod);
                    // });

                breadCrumb(total + ' date values')
            }

            selectedPeriod.subscribe(function(d) {
                if (!d) {
                    clearHighlight();
                }
            })

            // if(data){
            //     updateChart(data);
            // }
            if(!!configJSON){
                var root = partition(configJSON);
                total = configJSON.size;
                breadCrumb(total + ' date values');
    
                root.each(function(d) {
                    d.current = d;
                });
    
                // const svg = d3.create("svg")
                //     .attr("viewBox", [0, 0, width, width])
                //     .style("font", "10px sans-serif");
    
                // const g = svg.append("g")
                //     .attr("transform", `translate(${width / 2},${width / 2})`);

                var arc = d3.arc()
                    .startAngle(function(d){
                        return d.x0;
                    })
                    .endAngle(function(d){
                        return d.x1;
                    })
                    .padAngle(function(d){
                        return Math.min((d.x1 - d.x0) / 2, 0.005);
                    })
                    .padRadius(radius * 1.5)
                    // .innerRadius(function(d) {
                    //     return Math.max(0, y(d.y0));
                    // })
                    // .outerRadius(function(d) {
                    //     return Math.max(0, y(d.y0 + d.dy));
                    // });
                    .innerRadius(function(d) {
                        return d.y0 * radius;
                    })
                    .outerRadius(function(d) {
                        return Math.max(d.y0 * radius, d.y1 * radius - 1);
                    })

                // var arc = d3.arc()
                //     .startAngle(function(d) {
                //         return Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
                //     })
                //     .endAngle(function(d) {
                //         return Math.max(0, Math.min(2 * Math.PI, x(d.x0 + d.dx)));
                //     })
                //     .innerRadius(function(d) {
                //         return Math.max(0, y(d.y0));
                //     })
                //     .outerRadius(function(d) {
                //         return Math.max(0, y(d.y0 + d.dy));
                //     });
    
                var path = g.append("g")
                    .selectAll("path")
                    .data(root.descendants().slice(1))
                    .join("path")
                    .attr("fill", d => { while (d.depth > 1) d = d.parent; return colortheme(d.data.name); })
                    .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
                    .attr("d", d => arc(d.current))
                    .on("mouseover", highlightPeriod)
                    .call(clickmanager);
    
                path.filter(d => d.children)
                    .style("cursor", "pointer")

                var format = d3.format(",d");
    
                path.append("title")
                    .text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${format(d.value)}`);
    
                var label = g.append("g")
                    .attr("pointer-events", "none")
                    .attr("text-anchor", "middle")
                    .style("user-select", "none")
                    .selectAll("text")
                    .data(root.descendants().slice(1))
                    .join("text")
                    .attr("dy", "0.35em")
                    .attr("fill-opacity", d => +labelVisible(d.current))
                    .attr("transform", d => labelTransform(d.current))
                    .text(d => d.data.name);
    
                var parent = g.append("circle")
                    .datum(root)
                    .attr("r", radius)
                    .attr("fill", "none")
                    .attr("pointer-events", "all")
                    .call(clickmanager);
    
                function dblclick(p) {
                    parent.datum(p.parent || root);
    
                    root.each(d => d.target = {
                    x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
                    x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
                    y0: Math.max(0, d.y0 - p.depth),
                    y1: Math.max(0, d.y1 - p.depth)
                    });
    
                    var t = g.transition().duration(750);
    
                    // Transition the data on all arcs, even the ones that aren’t visible,
                    // so that if this transition is interrupted, entering arcs will start
                    // the next transition from the desired position.
                    path.transition(t)
                        .tween("data", d => {
                            var i = d3.interpolate(d.current, d.target);
                            return t => d.current = i(t);
                        })
                        .filter(function(d) {
                            return +this.getAttribute("fill-opacity") || arcVisible(d.target);
                        })
                        .attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0)
                        .attrTween("d", d => () => arc(d.current));
    
                    label.filter(function(d) {
                        return +this.getAttribute("fill-opacity") || labelVisible(d.target);
                    }).transition(t)
                        .attr("fill-opacity", d => +labelVisible(d.target))
                        .attrTween("transform", d => () => labelTransform(d.current));
                }
                
                function arcVisible(d) {
                    return true;
                    return d.y1 <= depth && d.y0 >= 1 && d.x1 > d.x0;
                }
    
                function labelVisible(d) {
                    return d.y1 <= depth && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03;
                }
    
                function labelTransform(d) {
                    var x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
                    var y = (d.y0 + d.y1) / 2 * radius;
                    return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
                }
            }

        }
    }
    return ko.bindingHandlers.timeWheel;
});
