define([
    'knockout',
    'jquery',
    'underscore',
    'arches',
    'd3'
], function(ko, $, _, arches, d3) {
    ko.bindingHandlers.relatedResourcesGraph = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var modelMap = arches.resources.reduce(function(a, v) {
                a[v.graphid] = v
                return a;
            }, {});
            var options = ko.unwrap(valueAccessor());
            var subscriptions = options.subscriptions;
            var nodeSelection = options.nodeSelection;
            var selectedState = ko.observable(false);
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
                .linkStrength(function(l, i) {
                    return 1;
                })
                .theta(0.8)
                .size([width, height]);

            var nodeList = options.nodeList
            var currentResource = options.currentResource

            var selectNode = function(d) {
                vis.selectAll("circle")
                    .attr("class", function(d1) {
                        var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                        if (d1 === d) {
                            className += '-selected';
                        } else if (linkMap[d1.id + '_' + d.id] || linkMap[d.id + '_' + d1.id]) {
                            className += '-neighbor';
                        }
                        return className;
                    });
                vis.selectAll("line")
                    .attr('class', function(l) {
                        return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                    });
                nodeSelection([d])
                updateNodeInfo(d);
            }

            var hoverNode = function(d) {
                vis.selectAll("circle")
                    .attr("class", function(d1) {
                        var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                        if (d1 === d) {
                            className += d1.selected() ? '-selected' : '-over';
                            if (selectedState() === false) {
                                nodeSelection([d1]);
                            }
                        } else if (linkMap[d1.id + '_' + d.id] || linkMap[d.id + '_' + d1.id]) {
                            if (d1.selected() === false) {
                                className += '-neighbor';
                            } else {
                                className += '-selected';
                            }
                        } else if (d1.selected()) {
                            className += '-selected';
                        }
                        return className;
                    });
                vis.selectAll("line")
                    .attr('class', function(l) {
                        return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                    });
            }

            var updateSelected = function(item) {
                var item = item;
                return function(val) {
                    selectedState(val);
                    if (val === true) {
                        selectNode(item);
                    } else {
                        nodeSelection.removeAll()
                        vis.selectAll("circle")
                            .attr("class", function(d1) {
                                return 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            });
                    }
                }
            }

            var updateHovered = function(item) {
                var item = item;
                return function(val) {
                    if (val === true) {
                        hoverNode(item);
                    } else {
                        if (selectedState() === false) {
                            nodeSelection.removeAll();
                        }
                    }
                }
            }

            nodeList.subscribe(function(list) {
                _.each(list, function(item) {
                    item.selected.subscribe(updateSelected(item), this)
                    item.hovered.subscribe(updateHovered(item), this)
                    if (item.relationCount) {
                        item.loaded(item.relationCount.loaded)
                        item.total(item.relationCount.total)
                    }
                })
            }, this)

            nodeList([])

            var redraw = function() {
                vis.attr("transform",
                    "translate(" + d3.event.translate + ")" +
                    " scale(" + d3.event.scale + ")");
            };

            var svg = d3.select(element).append("svg:svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", redraw));

            var vis = svg.append('svg:g');

            var update = function() {
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
                        var hoveredNodes = []
                        d3.select(this).attr("class", "linkMouseover");
                        vis.selectAll("circle").attr("class", function(d1) {
                            var matrix;
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d.source === d1 || d.target === d1) {
                                className += d1.selected() ? '-selected' : '-neighbor';
                                d1.relationship = (d.target === d1) ? d.relationshipTarget : d.relationshipSource;
                                matrix = this.getScreenCTM()
                                //transform svg coords to screen coords
                                d1.absX = matrix.a * d1.x + matrix.c * d1.y + matrix.e
                                d1.absY = matrix.b * d1.x + matrix.d * d1.y + matrix.f
                                hoveredNodes.push(d1);
                            } else if (d1.selected()) {
                                className += '-selected';
                            }
                            return className;
                        });
                        if (selectedState() === false) {
                            nodeSelection(hoveredNodes)
                        }
                    })
                    .on("mouseout", function(d) {
                        d3.select(this).attr("class", "link");
                        vis.selectAll("circle").attr("class", function(d1) {
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d1.selected()) {
                                className += '-selected';
                            }
                            return className;
                        });
                        if (selectedState() === false) {
                            nodeSelection.removeAll()
                        }
                    });
                link.exit()
                    .remove();

                var drag = force.drag()
                    .on("dragstart", function(d) {
                        d3.event.sourceEvent.stopPropagation();
                        d3.event.sourceEvent.preventDefault();
                    });

                var node = vis.selectAll("circle")
                    .data(data.nodes, function(d) {
                        return d.id;
                    });
                node.enter()
                    .append("circle")
                    .style('fill', function(d) {
                        return d.color;
                    })
                    .attr("r", function(d) {
                        return d.isRoot ? 24 : 18;
                    })
                    .attr("class", function(d) {
                        return 'node-' + (d.isRoot ? 'current' : 'ancestor');
                    })
                    .on("mouseover", function(d) {
                        vis.selectAll("circle")
                            .attr("class", function(d1) {
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1 === d) {
                                    className += d1.selected() ? '-selected' : '-over';
                                    _.each(nodeList(), function(n) {
                                        if (n.entityid === d.entityid) {
                                            n.hovered(true)
                                        } else {
                                            n.hovered(false)
                                        }
                                    })
                                } else if (linkMap[d1.id + '_' + d.id] || linkMap[d.id + '_' + d1.id]) {
                                    if (d1.selected() === false) {
                                        className += '-neighbor';
                                    } else {
                                        className += '-selected';
                                    }
                                } else if (d1.selected() === true) {
                                    className += '-selected';
                                }
                                return className;
                            });
                        vis.selectAll("line")
                            .attr('class', function(l) {
                                return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                            });
                    })
                    .on('mouseout', function(d) {
                        vis.selectAll("circle")
                            .attr("class", function(d1) {
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1.selected()) {
                                    className += '-selected';
                                }
                                _.each(nodeList(), function(n) {
                                    n.hovered(false)
                                    if (n.relationCount) {
                                        n.loaded(n.relationCount.loaded)
                                        n.total(n.relationCount.total)
                                    }
                                })
                                return className;
                            });
                        if (selectedState() === false) {
                            nodeSelection.removeAll()
                        }
                        vis.selectAll("line")
                            .attr('class', 'link');
                    })

                    .on("click", function(d) {
                        if (!d3.event.defaultPrevented) {
                            getResourceDataForNode(d);
                        }
                        vis.selectAll("circle")
                            .attr("class", function(d1) {
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1 === d) {
                                    _.each(nodeList(), function(n) {
                                        if (n.entityid === d.entityid) {
                                            if (n.selected() === false) {
                                                n.selected(true);
                                                className += '-selected';
                                            } else {
                                                n.selected(false);
                                            }
                                        } else {
                                            n.selected(false)
                                        }
                                    })
                                } else if (linkMap[d1.id + '_' + d.id] || linkMap[d.id + '_' + d1.id]) {
                                    className += '-neighbor';
                                }
                                return className;
                            });
                        vis.selectAll("line")
                            .attr('class', function(l) {
                                return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                            });
                        updateNodeInfo(d);
                    })
                    .call(drag);
                node.exit()
                    .remove();

                if (texts) {
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

                    texts
                        .attr("x", function(d) {
                            return d.x;
                        })
                        .attr("y", function(d) {
                            return d.y;
                        });

                });

                force.start();
            };

            var updateNodeInfo = function(d) {
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
                getResourceData(d.entityid, d.name, d.entitytypeid, function(newData) {
                    if (newData.nodes.length > 0 || newData.links.length > 0) {
                        data.nodes = data.nodes.concat(newData.nodes);
                        data.links = data.links.concat(newData.links);
                        update(data);
                    }
                }, false);
            };

            var getResourceData = function(resourceId, resourceName, resourceTypeId, callback, isRoot) {
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

                            if (isRoot) {
                                nodeSelection.removeAll();
                                selectedState(false);
                                rootNode = {
                                    id: newNodeId,
                                    entityid: resourceId,
                                    name: resourceName,
                                    entitytypeid: resourceTypeId,
                                    isRoot: true,
                                    relationType: 'Current',
                                    iconclass: response.node_config_lookup[response.resource_instance.graph_id].iconclass,
                                    color: response.node_config_lookup[response.resource_instance.graph_id].fillColor,
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

                            var getRelated = function(related_resource) {
                                var nodeConfigLookup = response.node_config_lookup;
                                if (!nodeMap[related_resource.resourceinstanceid]) {
                                    var node = {
                                        id: newNodeId,
                                        entityid: related_resource.resourceinstanceid,
                                        entitytypeid: related_resource.graph_id,
                                        name: related_resource.displayname,
                                        color: nodeConfigLookup[related_resource.graph_id].fillColor,
                                        iconclass: nodeConfigLookup[related_resource.graph_id].iconclass,
                                        isRoot: false,
                                        relationType: 'Ancestor',
                                        relationCount: {
                                            total: related_resource.total_relations,
                                            loaded: 1
                                        }
                                    };
                                    nodes.push(node);
                                    nodeMap[related_resource.resourceinstanceid] = node;
                                    newNodeId += 1;
                                }
                            }

                            _.each(response.related_resources, getRelated);

                            _.each(response.resource_relationships, function(resource_relationships) {
                                var sourceId = nodeMap[resource_relationships.resourceinstanceidfrom];
                                var targetId = nodeMap[resource_relationships.resourceinstanceidto];
                                var linkExists = _.find(data.links, function(link) {
                                    return (link.source === sourceId && link.target === targetId);
                                });
                                var relationshipSource = resource_relationships.relationshiptype_label;
                                var relationshipTarget = resource_relationships.relationshiptype_label;
                                if (resource_relationships.relationshiptype_label.split('/').length === 2) {
                                    relationshipSource = resource_relationships.relationshiptype_label.split('/')[0].trim();
                                    relationshipTarget = resource_relationships.relationshiptype_label.split('/')[1].trim();
                                }
                                if (!linkExists) {
                                    links.push({
                                        source: sourceId,
                                        target: targetId,
                                        relationshipSource: relationshipSource,
                                        relationshipTarget: relationshipTarget,
                                        weight: 1
                                    });
                                    linkMap[sourceId.id + '_' + targetId.id] = true;
                                }
                            });
                            nodeList(nodeList().concat(nodes))

                            callback({
                                nodes: nodes,
                                links: links
                            });
                        }
                    });
                }
            };

            setRoot = function(val) {
                if (val.graphid !== undefined) {
                    nodeMap = {};
                    linkMap = {};
                    nodeList([]);
                    getResourceData(val.resourceinstanceid, val.displayname, val.graphid, function(newData) {
                        $el.removeClass('loading');
                        data = newData;
                        data.nodes[0].x = width / 2;
                        data.nodes[0].y = height / 2 - 160;
                        update();
                    }, true);
                }
            };

            if (currentResource().resourceinstanceid) {
                setRoot(currentResource())
            }

            if (ko.isObservable(currentResource)) {
                var subscription = currentResource.subscribe(setRoot, this);
                if (subscriptions.length > 0) {
                    _.each(subscriptions, function(s) {
                        s.dispose()
                    })
                }
                subscriptions.push(subscription)
            }

            $(window).on("resize", function() {
                svg.attr("width", $el.parent().width());
            }).trigger("resize");

            $el.find('.load-more-relations-link').click(function() {
                getResourceDataForNode(selectedNode);
            })
        }
    };

    return ko.bindingHandlers.relatedResourcesGraph;
});
