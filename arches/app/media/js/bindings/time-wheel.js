define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'regenerator-runtime',
    'd3',
], function($, _, ko, arches, regeneratorRuntime, d3) {
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

            ko.utils.domData.set(element, 'vis', g);
        },

        update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            // see https://observablehq.com/@d3/zoomable-sunburst for the example that informed much of this code
            // also see http://bl.ocks.org/ropeladder/83915942ac42f17c087a82001418f2ee for the click/dblclick code

            var colortheme = d3.scaleOrdinal(d3.schemeCategory10);
            var $el = $(element);
            var opts = ko.unwrap(valueAccessor());
            var configJSON = opts.config();
            var breadCrumb = opts.breadCrumb;
            var selectedPeriod = opts.selectedPeriod;
            var total = 0;
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
            });

            var g = ko.utils.domData.get(element, 'vis');
            g.on("mouseleave", function(event) {
                var d = selectedPeriod();
                if (d) {
                    highlightPeriod(event, d);
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
                    .size([2 * Math.PI, root.height + 1])(root);
            };

            var d3ClickManager = function() {
                // we want to a distinguish single/double click
                // details http://bl.ocks.org/couchand/6394506
                var dispatcher = d3.dispatch('click', 'dblclick');
                function cc(selection) {
                    var down, tolerance = 5, last, wait = null, args;
                    // euclidean distance
                    function dist(a, b) {
                        return Math.sqrt(Math.pow(a[0] - b[0], 2), Math.pow(a[1] - b[1], 2));
                    }
                    selection.on('mousedown', function(event) {
                        down = d3.pointer(event);
                        last = +new Date();
                        args = arguments;
                    });
                    selection.on('mouseup', function(event) {
                        if (dist(down, d3.pointer(event)) > tolerance) {
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
                }
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
            };
            var clickmanager = d3ClickManager();
            clickmanager.on("click", function(event, d) {
                selectedPeriod(d);
            });

            function highlightPeriod(event, d) {
                let count = d.data.size;
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

                sequenceArray.push(count + ' hits');

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
                d3.selectAll("path")
                    .style("opacity", 1);
                breadCrumb(arches.translations.timeWheelDateMatches.replace("${total}", total));
            }

            selectedPeriod.subscribe(function(d) {
                if (!d) {
                    clearHighlight();
                }
            });

            if(!!configJSON){
                var root = partition(configJSON);
                total = configJSON.size;
                breadCrumb(arches.translations.timeWheelDateMatches.replace("${total}", total));
    
                root.each(function(d) {
                    d.current = d;
                });

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
                    .innerRadius(function(d) {
                        return d.y0 * radius;
                    })
                    .outerRadius(function(d) {
                        return Math.max(d.y0 * radius, d.y1 * radius - 1);
                    });

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
                    .style("cursor", "pointer");

                var format = d3.format(",d");
    
                path.append("title")
                    .text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${format(d.value)}`);
    
                var parent = g.append("circle")
                    .datum(root)
                    .attr("r", radius)
                    .attr("fill", "none")
                    .attr("pointer-events", "all")
                    .call(clickmanager);

                function arcVisible(d) {
                    return d.y1 <= depth && d.y0 >= 1 && d.x1 > d.x0;
                }

            }

        }
    };
    return ko.bindingHandlers.timeWheel;
});
