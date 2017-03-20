define([
    'knockout',
    'jquery',
    'underscore',
    'arches',
    'd3',
    'plugins/d3-tip'
], function (ko, $, _, arches, d3, d3Tip) {
    ko.bindingHandlers.relatedResourcesGraph = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var modelMap = arches.resources.reduce(function(a, v) {
                a[v.graphid] = v
                return a;
            }, {});
            var options = ko.unwrap(valueAccessor());
            var $el = $(element);
            var width = $el.parent().width();
            var height = $el.parent().height();
            var newNodeId = 0;
            var nodeMap = {};
            var linkMap = {};
            var data = {
                nodes: [],
                links: []
            };
            var texts;
            var selectedNode;
            var force = d3.layout.force()
                .charge(-500)
                .linkDistance(200)
                .gravity(0.05)
                .friction(0.55)
                .linkStrength(function(l, i) {return 1; })
                .theta(0.8)
                .size([width, height]);

            var redraw = function() {
                vis.attr("transform",
                    "translate(" + d3.event.translate + ")" +
                    " scale(" + d3.event.scale + ")");
                if (sourceTip) {
                    sourceTip.hide();
                }
                if (targetTip) {
                    targetTip.hide();
                }
                if (nodeTip) {
                    nodeTip.hide();
                }
            };

            var svg = d3.select(element).append("svg:svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", redraw));

            var vis = svg.append('svg:g');

            var sourceTip = d3Tip()
                .attr('class', 'd3-tip')
                .offset([-10, 0])
                .html(function (d) {
                    return  '<span class="graph-tooltip-name">' + d.name + "</span> " + d.relationship + "...</span>";
            });
            var targetTip = d3Tip()
                .attr('class', 'd3-tip')
                .direction('s')
                .offset([10, 0])
                .html(function (d) {
                    return  '<span class="graph-tooltip-name">' + d.name + "</span> " + d.relationship + "...</span>";
            });
            var nodeTip = d3Tip()
                .attr('class', 'd3-tip')
                .direction('n')
                .offset([-10, 0])
                .html(function (d) {
                    return  '<span class="graph-tooltip-name">' + d.name + "</span>";
            });

            vis.call(sourceTip)
                .call(targetTip)
                .call(nodeTip);
            var update = function () {
                data = {
                    nodes: force.nodes(data.nodes).nodes(),
                    links: force.links(data.links).links()
                };

                var link = vis.selectAll("line")
                    .data(data.links);
                link.enter()
                    .insert("line", "circle")
                    .attr("class", "link")
                    .on("mouseover", function(d) {
                        d3.select(this).attr("class", "linkMouseover");
                        vis.selectAll("circle").attr("class", function(d1){
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d.source === d1 || d.target === d1) {
                                var tip = (d.target === d1) ? targetTip : sourceTip;
                                className += '-neighbor';
                                d1.relationship = (d.target === d1) ? d.relationshipTarget : d.relationshipSource;
                                tip.show(d1, this);
                            } else if (d1 === selectedNode) {
                                className += '-over';
                            }
                            return className;
                        });
                    })
                    .on("mouseout", function(d) {
                        d3.select(this).attr("class", "link");
                        vis.selectAll("circle").attr("class", function(d1){
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d1 === selectedNode) {
                                className += '-over';
                            }
                            return className;
                        });
                        sourceTip.hide();
                        targetTip.hide();
                    });
                link.exit()
                    .remove();

                var drag = force.drag()
                    .on("dragstart", function(d) {
                        d3.event.sourceEvent.stopPropagation();
                        d3.event.sourceEvent.preventDefault();
                    });

                var node = vis.selectAll("circle")
                    .data(data.nodes, function(d) { return d.id; });
                node.enter()
                    .append("circle")
                    .attr("r",function(d){
                        return d.isRoot ? 24 : 18;
                    })
                    .attr("class", function(d){
                        return 'node-' + (d.isRoot ? 'current' : 'ancestor');
                    })
                    .on("mouseover", function(d){
                        vis.selectAll("circle")
                            .attr("class", function(d1){
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1 === d) {
                                    className += '-over';
                                } else if (linkMap[d1.id+'_'+d.id] || linkMap[d.id+'_'+d1.id]){
                                    className += '-neighbor';
                                }
                                return className;
                            });
                        vis.selectAll("line")
                            .attr('class', function(l) {
                                return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                            });
                        updateNodeInfo(d);
                        nodeTip.show(d, this);
                    })
                    .on('mouseout', function (d) {
                        vis.selectAll("circle")
                            .attr("class", function(d1){
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1 === selectedNode) {
                                    className += '-over';
                                }
                                return className;
                            });
                        vis.selectAll("line")
                            .attr('class', 'link');
                        nodeTip.hide();
                    })
                    .on("click", function (d) {
                        if (!d3.event.defaultPrevented){
                            getResourceDataForNode(d);
                        }
                    })
                    .call(drag);
                node.exit()
                    .remove();

                if (texts){
                    texts.remove();
                }

                texts = vis.selectAll("text.nodeLabels")
                    .data(data.nodes);

                texts.enter().append("text")
                    .attr("class", 'root-node-label')
                    .attr("dy", ".35em")
                    .text(function(d) {
                        return d.isRoot ? d.name : '';
                    });

                force.on("tick", function() {
                    link.attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });

                    node.attr("cx", function(d) { return d.x; })
                        .attr("cy", function(d) { return d.y; });

                    texts
                        .attr("x", function(d) { return d.x; })
                        .attr("y", function(d) { return d.y; });

                });

                force.start();
            };

            var updateNodeInfo = function (d) {
                var iconEl = $el.find('.resource-type-icon');
                $el.find('.selected-resource-name').html(d.name);
                $el.find('.selected-resource-name').attr('href', arches.urls.reports + d.entityid);
                $el.find('.resource-type-name').html(modelMap[d.entitytypeid].name);
                if (d.relationCount) {
                    $el.find('.relation-unloaded').hide();
                    $el.find('.relation-count').show();
                    $el.find('.relation-load-count').html(d.relationCount.loaded);
                    $el.find('.relation-total-count').html(d.relationCount.total);
                    if (d.relationCount.loaded === d.relationCount.total) {
                        $el.find('.load-more-relations-link').hide();
                    } else {
                        $el.find('.load-more-relations-link').show();
                    }
                } else {
                    $el.find('.load-more-relations-link').show();
                    $el.find('.relation-count').hide();
                    $el.find('.relation-unloaded').show();
                }
                iconEl.removeClass();
                iconEl.addClass('resource-type-icon');
                iconEl.addClass(modelMap[d.entitytypeid].icon);
                $el.find('.node_info').show();
                selectedNode = d;
            };

            var getResourceDataForNode = function(d) {
                getResourceData(d.entityid, d.name, d.entitytypeid, function (newData) {
                    if (newData.nodes.length > 0 || newData.links.length > 0) {
                        data.nodes = data.nodes.concat(newData.nodes);
                        data.links = data.links.concat(newData.links);
                        update(data);
                    }
                }, false);
            };

            var getResourceData = function (resourceId, resourceName, resourceTypeId, callback, isRoot) {
                var load = true;
                var start = 0;
                var rootNode = nodeMap[resourceId];

                if (rootNode) {
                    if (rootNode.relationCount) {
                        load = (rootNode.relationCount.total > rootNode.relationCount.loaded && !rootNode.loading);
                        start = rootNode.relationCount.loaded;
                    }
                }

                if (load) {
                    if (rootNode) {
                        rootNode.loading = true;
                    }
                    $.ajax({
                        url: arches.urls.related_resources + resourceId,
                        data: {
                            start: start
                        },
                        success: function(response) {
                            var links = [],
                                nodes = [];

                            if (isRoot){
                                rootNode = {
                                    id: newNodeId,
                                    entityid: resourceId,
                                    name: resourceName,
                                    entitytypeid: resourceTypeId,
                                    isRoot: true,
                                    relationType: 'Current',
                                    relationCount: {
                                        total: response.total,
                                        loaded: response.resource_relationships.length
                                    }
                                };
                                nodes.push(rootNode);
                                nodeMap[resourceId] = rootNode;
                                newNodeId += 1;
                            } else if (rootNode.relationCount) {
                                rootNode.relationCount.loaded = rootNode.relationCount.loaded + response.resource_relationships.length;
                            } else {
                                rootNode.relationCount = {
                                    total: response.total,
                                    loaded: response.resource_relationships.length
                                };
                            }
                            rootNode.loading = false;
                            updateNodeInfo(rootNode);
                            _.each(response.related_resources, function (related_resource) {
                                if (!nodeMap[related_resource.resourceinstanceid]) {
                                    var node = {
                                        id: newNodeId,
                                        entityid: related_resource.resourceinstanceid,
                                        entitytypeid: related_resource.graph_id,
                                        name: related_resource.displayname,
                                        isRoot: false,
                                        relationType: 'Ancestor',
                                        relationCount: null
                                    };
                                    nodes.push(node);
                                    nodeMap[related_resource.resourceinstanceid] = node;
                                    newNodeId += 1;
                                }
                            });

                            _.each(response.resource_relationships, function (resource_relationships) {
                                var sourceId = nodeMap[resource_relationships.resourceinstanceidfrom];
                                var targetId = nodeMap[resource_relationships.resourceinstanceidto];
                                var linkExists = _.find(data.links, function(link){
                                    return (link.source === sourceId && link.target === targetId);
                                });
                                var relationshipSource = resource_relationships.preflabel.value;
                                var relationshipTarget = resource_relationships.preflabel.value;
                                if (resource_relationships.preflabel.value.split('/').length === 2) {
                                    relationshipSource = resource_relationships.preflabel.value.split('/')[0].trim();
                                    relationshipTarget = resource_relationships.preflabel.value.split('/')[1].trim();
                                }
                                if (!linkExists) {
                                    links.push({
                                        source: sourceId,
                                        target: targetId,
                                        relationshipSource: relationshipSource,
                                        relationshipTarget: relationshipTarget,
                                        weight: 1
                                    });
                                    linkMap[sourceId.id+'_'+targetId.id] = true;
                                }
                            });

                            callback({
                                nodes: nodes,
                                links: links
                            });
                        }
                    });
                }
            };

            if (options.resourceId) {
                $el.addClass('loading');
                getResourceData(options.resourceId, options.resourceName, options.resourceTypeId, function (newData) {
                    $el.removeClass('loading');
                    data = newData;
                    data.nodes[0].x = width/2;
                    data.nodes[0].y = height/2-160;
                    update();
                }, true);
            }

            $(window).on("resize", function() {
                svg.attr("width", $el.parent().width());
            }).trigger("resize");

            $el.find('.load-more-relations-link').click(function () {
                getResourceDataForNode(selectedNode);
            })
        }
    };

    return ko.bindingHandlers.relatedResourcesGraph;
});
