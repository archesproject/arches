define([
    'knockout',
    'jquery',
    'underscore',
    'arches',
    'd3'
], function(ko, $, _, arches, d3) {
    ko.bindingHandlers.relatedResourcesGraph = {
        init: function(element, valueAccessor) {
            var modelMap = arches.resources.reduce(function(a, v) {
                a[v.graphid] = v;
                return a;
            }, {});
            var options = ko.unwrap(valueAccessor());
            var subscriptions = options.subscriptions;
            var nodeSelection = options.nodeSelection;
            var selectedState = ko.observable(false);
            var $el = $(element);
            var width = $el.parent().width() || 400;
            var height = $el.parent().height() || 400;
            var newNodeId = 0;
            var nodeMap = {};
            var linkMap = {};
            var data = {
                nodes: [],
                links: []
            };
            var texts;
            var selectedNode;

            var simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links))
                .force("charge", d3.forceCollide().radius(100))
                .force("radial", d3.forceRadial(300, width/2, height/2))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .alpha(0.01);
                
            var nodeList = options.nodeList;
            var currentResource = options.currentResource;

            var selectNode = function(d) {
                nodesElement.selectAll("circle")
                    .attr("class", function(d1) {
                        var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                        if (d1 === d) {
                            className += '-selected';
                        } else if (_.has(linkMap, d1.id + '_' + d.id) || _.has(linkMap, d.id + '_' + d1.id)) {
                            className += '-neighbor';
                        }
                        return className;
                    });
                linksElement.selectAll("line")
                    .attr('class', function(l) {
                        return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                    });
                nodeSelection([d]);
                updateNodeInfo(d);
            };

            var clearHover = function(d) {
                linksElement.selectAll("line")
                    .attr('class', function(l) {
                        return 'link';
                    });
                nodesElement.selectAll("circle").attr("class", function(d1) {
                    var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                    if (d1.selected()) {
                        className += '-selected';
                    }
                    return className;
                });
            };

            var hoverNode = function(d) {
                nodesElement.selectAll("circle")
                    .attr("class", function(d1) {
                        var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                        if (d1 === d) {
                            className += d1.selected() ? '-selected' : '-over';
                            if (selectedState() === false) {
                                nodeSelection([d1]);
                            }
                        } else if (_.has(linkMap, d1.id + '_' + d.id) || _.has(linkMap, d.id + '_' + d1.id)) {
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
                linksElement.selectAll("line")
                    .attr('class', function(l) {
                        return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                    });
            };

            var updateSelected = function(item) {
                return function(val) {
                    selectedState(val);
                    if (val === true) {
                        selectNode(item);
                    } else {
                        nodeSelection.removeAll();
                        nodesElement.selectAll("circle")
                            .attr("class", function(d1) {
                                return 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            });
                    }
                };
            };

            var updateHovered = function(item) {
                return function(val) {
                    if (val === true) {
                        hoverNode(item);
                    } else {
                        clearHover(item);
                        if (selectedState() === false) {
                            nodeSelection.removeAll();
                        }
                    }
                };
            };

            var svg = d3.select(element).append("svg:svg")
                .attr("viewBox", [0, 0, width, height])
                .call(d3.zoom()
                    .extent([[0, 0], [width, height]])
                    .scaleExtent([0.25, 8])
                    .on("zoom", function(event) {
                        groupElement.attr("transform", event.transform);
                    }));

            var groupElement = svg.append('svg:g');
            var linksElement = groupElement.append('svg:g');
            var nodesElement = groupElement.append('svg:g');

            var update = function() {
                var linkMap = linkMap;

                $(window).trigger("resize");
                simulation.nodes(data.nodes);
                simulation.force("link").links(data.links);
                simulation.alpha(0.01).restart();

                var link = linksElement.selectAll("line")
                    .data(data.links)
                    .join("line")
                    .attr("class", "link")
                    .on("mouseover", function(event, d) {
                        var hoveredNodes = [];
                        var linkMap = linkMap;
                        d3.select(this).attr("class", "linkMouseover");
                        nodesElement.selectAll("circle").attr("class", function(d1) {
                            var matrix;
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d.source === d1 || d.target === d1) {
                                className += d1.selected() ? '-selected' : '-neighbor';
                                d1.relationship = (d.target === d1) ? d.relationshipTarget : d.relationshipSource;
                                d1.relationships = d.all_relationships;
                                matrix = this.getScreenCTM();
                                //transform svg coords to screen coords
                                d1.absX = matrix.a * d1.x + matrix.c * d1.y + matrix.e;
                                d1.absY = matrix.b * d1.x + matrix.d * d1.y + matrix.f;
                                hoveredNodes.push(d1);
                            } else if (d1.selected()) {
                                className += '-selected';
                            }
                            return className;
                        });
                        nodeSelection(hoveredNodes);
                    })
                    .on("mouseout", function(event, d) {
                        d3.select(this).attr("class", "link");
                        nodesElement.selectAll("circle").attr("class", function(d1) {
                            var className = 'node-' + (d1.isRoot ? 'current' : 'ancestor');
                            if (d1.selected()) {
                                className += '-selected';
                            }
                            return className;
                        });
                        nodeSelection.removeAll();
                    });
                link.exit()
                    .remove();

                var node = nodesElement.selectAll("circle")
                    .data(data.nodes, function(d) {
                        return d.id;
                    })
                    .join("circle")
                    .style('fill', function(d) {
                        return d.color;
                    })
                    .attr("r", function(d) {
                        return d.isRoot ? 24 : 18;
                    })
                    .attr("class", function(d) {
                        return 'node-' + (d.isRoot ? 'current' : 'ancestor');
                    })
                    .on("mouseover", function(event, d) {
                        nodesElement.selectAll("circle")
                            .attr("class", function(d1) {
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1 === d) {
                                    className += d1.selected() ? '-selected' : '-over';
                                    _.each(nodeList(), function(n) {
                                        if (n.entityid === d.entityid) {
                                            n.hovered(true);
                                        } else {
                                            n.hovered(false);
                                        }
                                    });
                                } else if (_.has(linkMap, d1.id + '_' + d.id) || _.has(linkMap, d.id + '_' + d1.id)) {
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
                        linksElement.selectAll("line")
                            .attr('class', function(l) {
                                return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                            });
                    })
                    .on('mouseout', function(event, d) {
                        nodesElement.selectAll("circle")
                            .attr("class", function(d1) {
                                var className = 'node-' + (d.isRoot ? 'current' : 'ancestor');
                                if (d1.selected()) {
                                    className += '-selected';
                                }
                                _.each(nodeList(), function(n) {
                                    n.hovered(false);
                                    if (n.relationCount) {
                                        n.loaded(n.relationCount.loaded);
                                        n.total(n.relationCount.total);
                                    }
                                });
                                return className;
                            });
                        if (selectedState() === false) {
                            nodeSelection.removeAll();
                        }
                        linksElement.selectAll("line")
                            .attr('class', 'link');
                    })
                    .on("click", function(event, d) {
                        if (!event.defaultPrevented) {
                            d.loadcount(d.loadcount()+1);
                        }
                        nodesElement.selectAll("circle")
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
                                            n.selected(false);
                                        }
                                    });
                                } else if (_.has(linkMap, d1.id + '_' + d.id) || _.has(linkMap, d.id + '_' + d1.id)) {
                                    className += '-neighbor';
                                }
                                return className;
                            });
                        linksElement.selectAll("line")
                            .attr('class', function(l) {
                                return (l.source === d || l.target === d) ? 'linkMouseover' : 'link';
                            });
                        updateNodeInfo(d);
                    })
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended)
                    );

                function dragstarted(event, d) {
                    if (!event.active) { simulation.alphaTarget(0.01).restart(); }
                    d.fx = d.x;
                    d.fy = d.y;
                }
                
                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }
                
                function dragended(event, d) {
                    if (!event.active) { simulation.alphaTarget(0); }
                    d.fx = null;
                    d.fy = null;
                }    

                if (texts) {
                    texts.remove();
                }

                texts = nodesElement.selectAll("text.nodeLabels")
                    .data(data.nodes)
                    .join("text")
                    .attr("class", function(d){
                        return d.isRoot ? 'root-node-label' : 'nodeLabels';
                    })
                    .attr("dy", ".35em")
                    .text(function(d) {
                        return d.name;
                    });

                simulation.on("tick", function() {
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
                        })
                        .attr("x", function() {
                            return width / 2;
                        })
                        .attr("y", function() {
                            return height / 2;
                        });
                    texts
                        .attr("x", function(d) {
                            return d.x;
                        })
                        .attr("y", function(d) {
                            return d.y;
                        });

                });
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

            var getMoreData = function(item) {
                return function(val) {
                    if (val) {
                        getResourceDataForNode(item);
                    }
                };
            };

            var getResourceData = function(resourceId, resourceName, resourceTypeId, callback, isRoot) {
                var load = true;
                var start = 0;
                var page = 1;
                var rootNode = nodeMap[resourceId];

                if (rootNode) {
                    if (rootNode.relationCount) {
                        load = (rootNode.relationCount.total > rootNode.relationCount.loaded && !rootNode.loading);
                        start = rootNode.relationCount.loaded;
                        page = rootNode.loadcount();
                    }
                }
                if (load) {
                    if (rootNode) {
                        rootNode.loading = true;
                    }

                    $.ajax({
                        url: arches.urls.related_resources + resourceId,
                        data: {
                            start: start,
                            page: page > 0 ? page : 1
                        },
                        error: function(e) {
                            // eslint-disable-next-line no-console
                            console.log('request failed', e);
                        },
                        success: function(response) {
                            var links = [];
                            var nodes = [];
                            var rr = response.related_resources;
                            var totalLoaded;
                            if (isRoot) {
                                nodeSelection.removeAll();
                                selectedState(false);
                                rootNode = {
                                    id: newNodeId,
                                    entityid: resourceId,
                                    name: resourceName,
                                    description: rr.resource_instance.displaydescription,
                                    entitytypeid: resourceTypeId,
                                    isRoot: true,
                                    relationType: 'Current',
                                    graphname: rr.node_config_lookup[rr.resource_instance.graph_id].name,
                                    iconclass: rr.node_config_lookup[rr.resource_instance.graph_id].iconclass,
                                    color: rr.node_config_lookup[rr.resource_instance.graph_id].fillColor,
                                    relationCount: {
                                        total: rr.total.value,
                                        loaded: rr.resource_relationships.length
                                    }
                                };
                                nodes.push(rootNode);
                                nodeMap[resourceId] = rootNode;
                                newNodeId += 1;
                            } else if (rootNode.relationCount) {
                                totalLoaded = rootNode.relationCount.loaded + rr.resource_relationships.length;
                                rootNode.relationCount.loaded = totalLoaded <= rr.total.value ? totalLoaded : rr.total.value;
                            } else {
                                rootNode.relationCount = {
                                    total: rr.total.value,
                                    loaded: rr.resource_relationships.length
                                };
                            }
                            rootNode.loading = false;
                            updateNodeInfo(rootNode);

                            var getRelated = function(relatedResource) {
                                var nodeConfigLookup = rr.node_config_lookup;
                                if (!nodeMap[relatedResource.resourceinstanceid]) {
                                    var node = {
                                        id: newNodeId,
                                        entityid: relatedResource.resourceinstanceid,
                                        entitytypeid: relatedResource.graph_id,
                                        name: relatedResource.displayname,
                                        description: relatedResource.displaydescription,
                                        color: nodeConfigLookup[relatedResource.graph_id].fillColor,
                                        iconclass: nodeConfigLookup[relatedResource.graph_id].iconclass,
                                        graphname: nodeConfigLookup[relatedResource.graph_id].name,
                                        isRoot: false,
                                        relationType: 'Ancestor',
                                        relationCount: {
                                            total: relatedResource.total_relations.value,
                                            loaded: 1
                                        }
                                    };
                                    nodes.push(node);
                                    nodeMap[relatedResource.resourceinstanceid] = node;
                                    newNodeId += 1;
                                }
                            };
                            _.each(rr.related_resources, getRelated);

                            _.each(rr.resource_relationships, function(resourceRelationships) {
                                var sourceId = nodeMap[resourceRelationships.resourceinstanceidfrom];
                                var targetId = nodeMap[resourceRelationships.resourceinstanceidto];
                                var relationshipSource = resourceRelationships.relationshiptype_label;
                                var relationshipTarget = resourceRelationships.relationshiptype_label;
                                if (resourceRelationships.relationshiptype_label.split('/').length === 2) {
                                    relationshipSource = resourceRelationships.relationshiptype_label.split('/')[0].trim();
                                    relationshipTarget = resourceRelationships.relationshiptype_label.split('/')[1].trim();
                                }

                                links.push({
                                    source: sourceId,
                                    target: targetId,
                                    relationshipSource: relationshipSource,
                                    relationshipTarget: relationshipTarget,
                                    weight: 1
                                });

                                if (!_.has(linkMap, [sourceId.id + '_' + targetId.id])) {
                                    linkMap[sourceId.id + '_' + targetId.id] = {relationships:[]};
                                }
                                if (!_.has(linkMap, [targetId.id + '_' + sourceId.id])) {
                                    linkMap[targetId.id + '_' + sourceId.id] = {relationships:[]};
                                }
                                if (_.contains(linkMap[sourceId.id + '_' + targetId.id]['relationships'], relationshipSource) === false) {
                                    linkMap[sourceId.id + '_' + targetId.id]['relationships'].push(relationshipSource);
                                }
                                if (_.contains(linkMap[targetId.id + '_' + sourceId.id]['relationships'], relationshipSource) === false) {
                                    linkMap[targetId.id + '_' + sourceId.id]['relationships'].push(relationshipSource);
                                }
                            });

                            var links = _.uniq(links, function(item, key, source) {
                                return item.source.id + '_' + item.target.id;
                            });

                            _.each(links, function(l){
                                if (_.has(linkMap, l.source.id + '_' + l.target.id)) {
                                    l.all_relationships = linkMap[l.source.id + '_' + l.target.id].relationships;
                                }
                            });

                            nodeList(nodeList().concat(nodes));

                            callback({
                                nodes: nodes,
                                links: links
                            });
                        }
                    });
                }
            };

            var setRoot = function(val) {
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
                setRoot(currentResource());
            }

            if (ko.isObservable(currentResource)) {
                var subscription = currentResource.subscribe(setRoot, this);
                if (subscriptions.length > 0) {
                    _.each(subscriptions, function(s) {
                        s.dispose();
                    });
                }
                subscriptions.push(subscription);
            }

            $(window).on("resize", function() {
                var w = $el.parent().width();
                var h = $el.parent().height();
                svg.attr("width", w);
                svg.attr("height", h);
                svg.attr("viewBox", [0, 0, w, h]);
            }).trigger("resize");


            nodeList.subscribe(function(list) {
                _.each(list, function(item) {
                    if (item.selectedSubscription) {
                        item.selectedSubscription.dispose();
                        item.hoveredSubscription.dispose();
                        item.loadcountSubscription.dispose();
                    }
                    item.selectedSubscription = item.selected.subscribe(updateSelected(item), this);
                    item.hoveredSubscription = item.hovered.subscribe(updateHovered(item), this);
                    if (item.isRoot && item.loadcount() === 0) {
                        item.loadcount(1);
                    }
                    item.loadcountSubscription = item.loadcount.subscribe(getMoreData(item), this);

                    if (item.relationCount) {
                        item.loaded(item.relationCount.loaded);
                        item.total(item.relationCount.total);
                    }
                });
            }, this);

            nodeList([]);
        }
    };
    return ko.bindingHandlers.relatedResourcesGraph;
});
