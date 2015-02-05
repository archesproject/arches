define(['jquery', 'backbone', 'underscore', 'arches', 'resource-types', 'd3'], function($, Backbone, _, arches, resourceTypes) {
    var colorLuminance = function(hex, lum) {
        hex = String(hex).replace(/[^0-9a-f]/gi, '');
        if (hex.length < 6) {
            hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
        }
        lum = lum || 0;

        var rgb = "#", c, i;
        for (i = 0; i < 3; i++) {
            c = parseInt(hex.substr(i*2,2), 16);
            c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
            rgb += ("00"+c).substr(c.length);
        }

        return rgb;
    };

    return Backbone.View.extend({
        resourceId: null,
        resourceName: '',
        resourceTypeId: '',
        newNodeId: 0,
        events: {
            'click .load-more-relations-link': 'loadMoreRelations'
        },

        initialize: function(options) {
            var self = this,
                width = this.$el.parent().width(),
                height = 400;

            _.extend(this, _.pick(options, 'resourceId', 'resourceName', 'resourceTypeId'));
            this.nodeIdMap = {};
            this.linkMap = {};
            this.data = {
                nodes: [],
                links: []
            };
            var canvasd3 = $(".arches-search-item-description");

            $(window).on("resize", function() {
                canvasd3.attr("width", canvasd3.parent().width());
                canvasd3.attr("height", canvasd3.parent().height());
            }).trigger("resize");

            self.force = d3.layout.force()
                .charge(-2750)
                .linkDistance(200)
                .gravity(0.05)
                .friction(0.55)
                .linkStrength(function(l, i) {return 1; })
                .theta(0.8)
                .size([width, height]);

            var redraw = function() {
                self.vis.attr("transform",
                    "translate(" + d3.event.translate + ")" +
                    " scale(" + d3.event.scale + ")");
                if (self.sourceTip) {
                    self.sourceTip.hide();
                }
                if (self.targetTip) {
                    self.targetTip.hide();
                }
                if (self.nodeTip) {
                    self.nodeTip.hide();
                }
            };

            self.svg = d3.select(this.el).append("svg:svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", redraw));
            self.vis = self.svg.append('svg:g');

            require(['plugins/d3-tip'], function (d3Tip) {
                sourceTip = d3Tip()
                    .attr('class', 'd3-tip')
                    .offset([-10, 0])
                    .html(function (d) {
                        return  '<span class="graph-tooltip-name">' + d.name + "</span> " + d.relationship + "...</span>";
                });
                targetTip = d3Tip()
                    .attr('class', 'd3-tip')
                    .direction('s')
                    .offset([10, 0])
                    .html(function (d) {
                        return  '<span class="graph-tooltip-name">' + d.name + "</span> " + d.relationship + "...</span>";
                });
                nodeTip = d3Tip()
                    .attr('class', 'd3-tip')
                    .direction('n')
                    .offset([-10, 0])
                    .html(function (d) {
                        return  '<span class="graph-tooltip-name">' + d.name + "</span>";
                });
                self.sourceTip = sourceTip;
                self.targetTip = targetTip;
                self.nodeTip = nodeTip;
                self.vis.call(sourceTip);
                self.vis.call(targetTip);
                self.vis.call(nodeTip);
            });

            if (self.resourceId) {
                self.$el.addClass('loading');
                self.getResourceData(self.resourceId, this.resourceName, self.resourceTypeId, function (data) {
                    self.$el.removeClass('loading');
                    self.data = data;
                    self.data.nodes[0].fixed = true;
                    self.data.nodes[0].x = width/2;
                    self.data.nodes[0].y = height/2;
                    self.update();
                }, true);
            }

            self.$el.addClass('view-created');
        },

        update: function () {
            var self = this;

            self.data = {
                nodes: self.force.nodes(self.data.nodes).nodes(),
                links: self.force.links(self.data.links).links()
            };

            var link = self.vis.selectAll("line")
                .data(self.data.links);

            var linkEnter = link.enter().insert("line", "circle")
                .attr("class", "link")
                .on("mouseover", function(d) {
                    d3.select(this).attr("class", "linkMouseover");

                    self.vis.selectAll("circle").attr("class", function(d1){
                        var className = "node-descendent";
                        if(d1.relationType == "Current"){
                            className = "node-current";
                        } else if (d1.relationType == "Ancestor"){
                            className = "node-ancestor";
                        }
                        if (d.source === d1) {
                            className += '-neighbor';
                            if (self.sourceTip) {
                                d1.relationship = d.relationshipSource;
                                self.sourceTip.show(d1, this);
                            }
                        } else if (d.target === d1) {
                            className += '-neighbor';
                            if (self.targetTip) {
                                d1.relationship = d.relationshipTarget;
                                self.targetTip.show(d1, this);
                            }
                        } else if (d1 === self.selectedNode) {
                            className += '-over';
                        } 
                        return className;
                    });
                })
                .on("mouseout", function(d) {
                    d3.select(this)
                    .attr("class", "link");
                    self.vis.selectAll("circle").attr("class", function(d1){
                        var className = "node-descendent";
                        if(d1.relationType == "Current"){
                            className = "node-current";
                        } else if (d1.relationType == "Ancestor"){
                            className = "node-ancestor";
                        }
                        if (d1 === self.selectedNode) {
                            className += '-over';
                        }
                        if (self.sourceTip) {
                            self.sourceTip.hide();
                        }
                        if (self.targetTip) {
                            self.targetTip.hide();
                        }
                        return className;
                    });
                });

            link.exit().remove();

            var drag = self.force.drag()
              .on("dragstart", function(d) {
                d3.event.sourceEvent.stopPropagation();
              });

            var node = self.vis.selectAll("circle")
                .data(self.data.nodes, function(d) { return d.id; });

            var nodeEnter = node.enter().append("circle")
                .attr("r",function(d){
                    if(d.relationType == "Current"){
                        return 24;
                    } else if (d.relationType == "Ancestor"){
                        return 18;
                    } else {
                        return 8;
                    }
                })
                .attr("r",function(d){
                    if(d.relationType == "Current"){
                        return 30;
                    } else if (d.relationType == "Ancestor"){
                        return 22;
                    } else {
                        return 16;
                    }
                })
                .attr("class", function(d){
                    if(d.relationType == "Current"){
                        return "node-current";
                    } else if (d.relationType == "Ancestor"){
                        return "node-ancestor";
                    } else {
                        return "node-descendent";
                    }
                }).attr("style", function(d){
                    return "fill:" + resourceTypes[d.entitytypeid].color + ";stroke:" + colorLuminance(resourceTypes[d.entitytypeid].color, -0.3);
                })
                .on("mouseover", function(d){
                    self.vis.selectAll("circle").attr("class", function(d1){
                        var className = "node-descendent";
                        if(d1.relationType == "Current"){
                            className = "node-current";
                        } else if (d1.relationType == "Ancestor"){
                            className = "node-ancestor";
                        }
                        if (d1 === d) {
                            className += '-over';
                        } else if (self.linkMap[d1.id+'_'+d.id] || self.linkMap[d.id+'_'+d1.id]){
                            className += '-neighbor';
                        }
                        return className;
                    }).attr("style", function(d1){
                        return "fill:" + resourceTypes[d1.entitytypeid].color + ";stroke:" + colorLuminance(resourceTypes[d1.entitytypeid].color, -0.3);
                    });
                    self.vis.selectAll("line").attr('class', function(l) {
                        if (l.source === d || l.target === d) {
                            return 'linkMouseover';
                        } else {
                            return 'link';
                        }
                    });
                    self.updateNodeInfo(d);
                    if (self.nodeTip) {
                        self.nodeTip.show(d, this);
                    }
                })
                .on('mouseout', function (d) {
                    self.vis.selectAll("circle").attr("class", function(d1){
                        var className = "node-descendent";
                        if(d1.relationType == "Current"){
                            className = "node-current";
                        } else if (d1.relationType == "Ancestor"){
                            className = "node-ancestor";
                        }
                        if (d1 === d) {
                            className += '-over';
                        }
                        return className;
                    });
                    self.vis.selectAll("line").attr('class', function(l) {
                        return 'link';
                    });
                    if (self.nodeTip) {
                        self.nodeTip.hide();
                    }
                })
                .on("click", function (d) {
                    self.getResourceDataForNode(d);
                })
                .call(drag);

            node.exit().remove();

            self.force.on("tick", function() {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });
         
                node
                    .attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; });
         
            });

            self.force.start();
        },

        getResourceDataForNode: function(d) {
            var self = this;
            self.getResourceData(d.entityid, d.name, d.entitytypeid, function (newData) {
                if (newData.nodes.length > 0 || newData.links.length > 0) {
                    self.data.nodes = self.data.nodes.concat(newData.nodes);
                    self.data.links = self.data.links.concat(newData.links);
                    self.update(self.data);
                }
            }, false);
        },

        loadMoreRelations: function () {
            this.getResourceDataForNode(this.selectedNode);
        },

        updateNodeInfo: function (d) {
            var self = this;
            self.$el.find('.selected-resource-name').html(d.name);
            self.$el.find('.selected-resource-name').attr('href', arches.urls.reports + d.entityid);
            self.$el.find('.resource-type-name').html(resourceTypes[d.entitytypeid].name);
            if (d.relationCount) {
                self.$el.find('.relation-unloaded').hide();
                self.$el.find('.relation-count').show();
                self.$el.find('.relation-load-count').html(d.relationCount.loaded);
                self.$el.find('.relation-total-count').html(d.relationCount.total);
                if (d.relationCount.loaded === d.relationCount.total) {
                    self.$el.find('.load-more-relations-link').hide();
                } else { 
                    self.$el.find('.load-more-relations-link').show();
                }
            } else {
                self.$el.find('.load-more-relations-link').show();
                self.$el.find('.relation-count').hide();
                self.$el.find('.relation-unloaded').show();
            }
            var iconEl = self.$el.find('.resource-type-icon');
            iconEl.removeClass();
            iconEl.addClass('resource-type-icon');
            iconEl.addClass(resourceTypes[d.entitytypeid].icon);
            self.$el.find('.node_info').show();
            self.selectedNode = d;
        },

        getResourceData: function (resourceId, resourceName, resourceTypeId, callback, includeRoot) {
            var load = true;
            var self = this;
            var start = 0;
            var rootNode = this.nodeIdMap[resourceId];

            if (rootNode) {
                if (rootNode.relationCount) {
                    load = (rootNode.relationCount.total > rootNode.relationCount.loaded);
                    start = rootNode.relationCount.loaded;
                }
            }

            if (load) {
                $.ajax({
                    url: arches.urls.related_resources + resourceId,
                    data: {
                        start: start
                    },
                    success: function(response) {
                        var links = [],
                            nodes = [];

                        if (includeRoot){
                            rootNode = {
                                id: self.newNodeId,
                                entityid: resourceId,
                                name: resourceName,
                                entitytypeid: resourceTypeId,
                                relationType: 'Current',
                                relationCount: {
                                    total: response.total,
                                    loaded: response.resource_relationships.length
                                }
                            };
                            nodes.push(rootNode);
                            self.nodeIdMap[resourceId] = rootNode;
                            self.newNodeId += 1;
                        } else if (rootNode.relationCount) {
                            rootNode.relationCount.loaded = rootNode.relationCount.loaded + response.resource_relationships.length;
                        } else {
                            rootNode.relationCount = {
                                total: response.total,
                                loaded: response.resource_relationships.length
                            };
                        }
                        self.updateNodeInfo(rootNode);
                        _.each(response.related_resources, function (related_resource) {
                            if (!self.nodeIdMap[related_resource.entityid]) {
                                var node = {
                                    id: self.newNodeId,
                                    entityid: related_resource.entityid,
                                    entitytypeid: related_resource.entitytypeid,
                                    name: related_resource.primaryname,
                                    relationType: 'Ancestor',
                                    relationCount: null
                                };
                                nodes.push(node);
                                self.nodeIdMap[related_resource.entityid] = node;
                                self.newNodeId += 1;
                            }
                        });

                        _.each(response.resource_relationships, function (resource_relationships) {
                            var sourceId = self.nodeIdMap[resource_relationships.entityid1];
                            var targetId = self.nodeIdMap[resource_relationships.entityid2];
                            var linkExists = _.find(self.data.links, function(link){
                                return (link.source === sourceId && link.target === targetId);
                            });
                            if (!linkExists) {
                                links.push({
                                    source: sourceId,
                                    target: targetId,
                                    relationshipSource: resource_relationships.preflabel.value.split('/')[0].trim(),
                                    relationshipTarget: resource_relationships.preflabel.value.split('/')[1].trim(),
                                    weight: 1
                                });
                                self.linkMap[sourceId.id+'_'+targetId.id] = true;
                            }
                        });

                        callback({
                            nodes: nodes,
                            links: links
                        });
                    }
                });
            }
        }
    });
});

