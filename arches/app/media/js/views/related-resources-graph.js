define(['jquery', 'backbone', 'underscore', 'arches', 'resource-types', 'd3'], function($, Backbone, _, arches, resourceTypes) {
    return Backbone.View.extend({
        resourceId: null,
        resourceName: '',
        resourceTypeId: '',
        newNodeId: 0,

        initialize: function(options) {
            var self = this;

            _.extend(this, _.pick(options, 'resourceId', 'resourceName', 'resourceTypeId'));
            this.nodeIdMap = {};
            this.data = {
                nodes: [],
                links: []
            };

            if (self.resourceId) {
                self.$el.addClass('loading');
                self.getResourceData(self.resourceId, this.resourceName, self.resourceTypeId, function (data) {
                    self.$el.removeClass('loading');
                    self.data = data;
                    self.render();
                }, true);
            }
        },
        render: function () {
            var self = this,
                width = this.$el.parent().width(),
                height = 400;

            self.force = d3.layout.force()
                .charge(-2750)
                .linkDistance(200)
                .gravity(0.05)
                .friction(0.55)
                .linkStrength(function(l, i) {return 1; })
                .theta(0.8)
                .size([width, height]);

            var redraw = function() {
                self.svg.attr("transform",
                    "translate(" + d3.event.translate + ")" +
                    " scale(" + d3.event.scale + ")");
            };

            self.svg = d3.select(this.el).append("svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", redraw))
                .append('svg:g');

            self.svg.append("defs").selectAll("marker")
                .data(["suit", "licensing", "resolved"])
              .enter().append("marker")
                .attr("id", function(d) { return d; })
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 25)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
              .append("path")
                .attr("d", "M0,-5L10,0L0,5 L10,0 L0, -5")
                .style("stroke", "#b3b3b3")
                .style("opacity", "0.6");

            self.data.nodes[0].fixed = true;
            self.data.nodes[0].x = width/2;
            self.data.nodes[0].y = height/2;


            var canvasd3 = $(".arches-search-item-description"),
                aspect = canvasd3.width() / canvasd3.height(),
                containerd3 = canvasd3.parent();

            $(window).on("resize", function() {
                var targetWidth = containerd3.width();
                var targetHeight = containerd3.height();
                canvasd3.attr("width", targetWidth);
                canvasd3.attr("height", targetHeight);
            }).trigger("resize");

            self.update(self.data);

            self.$el.addClass('view-created');
        },

        update: function () {
            var self = this;
            self.data = {
                nodes: self.force.nodes(self.data.nodes).nodes(),
                links: self.force.links(self.data.links).links()
            };

            var link = self.svg.selectAll(".link")
                .data(self.data.links);

            link.enter().insert("line", "circle")
                .attr("class", "link")
                .style("marker-end",  "url(#suit)")
                .on("mouseover", function(d) {
                    d3.select(this).attr("class", "linkMouseover");
                    link.append("title").text(function(d) {
                        return d.relationship;
                    });
                })
                .on("mouseout", function(d) {
                    d3.select(this)
                    .attr("class", "link");
                });

            link.exit().remove();

            var node = self.svg.selectAll("circle")
                .data(self.data.nodes, function(d) { return d.id; });

            nodeEnter = node.enter().append("circle")
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
                    return "fill:" + resourceTypes[d.entitytypeid].color
                })
                .on("mouseover", function(d){
                    self.svg.selectAll("circle").attr("class", function(d){
                        if(d.relationType == "Current"){
                            return "node-current";
                        } else if (d.relationType == "Ancestor"){
                            return "node-ancestor";
                        } else {
                            return "node-descendent";
                        }
                    });
                    d3.select(this).attr("class", function(d) {
                        if (d.relationType == "Current") {
                            return "node-current-over";
                        } else if (d.relationType == "Ancestor") {
                            return "node-ancestor-over";
                        } else {
                            return "node-descendent-over";
                        }
                    });
                    self.$el.find('.selected-resource-name').html(d.name);
                    self.$el.find('.selected-resource-name').attr('href', arches.urls.reports + d.entityid);
                    self.$el.find('.resource-type-name').html(resourceTypes[d.entitytypeid].name);
                    var iconEl = self.$el.find('.resource-type-icon');
                    iconEl.removeClass();
                    iconEl.addClass('resource-type-icon');
                    iconEl.addClass(resourceTypes[d.entitytypeid].icon);
                    self.$el.find('.node_info').show();
                })
                .on("click", function (d) {
                    self.getResourceData(d.entityid, d.name, d.entitytypeid, function (newData) {
                        if (newData.nodes.length > 0 || newData.links.length > 0) {
                            self.data.nodes = self.data.nodes.concat(newData.nodes);
                            self.data.links = self.data.links.concat(newData.links);
                            self.update(self.data);
                        }
                    }, false);
                })

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
            node.call(self.force.drag);
        },

        getResourceData: function (resourceId, resourceName, resourceTypeId, callback, includeRoot) {
            var self = this;
            $.ajax({
                url: arches.urls.related_resources + resourceId,
                success: function(response) {
                    var links = [],
                        nodes = [];

                    if (includeRoot){
                        var node = {
                            id: self.newNodeId,
                            entityid: resourceId,
                            name: resourceName,
                            entitytypeid: resourceTypeId,
                            relationType: 'Current'
                        };
                        nodes.push(node);
                        self.nodeIdMap[resourceId] = node;
                        self.newNodeId += 1;
                    }
                    _.each(response.related_resources, function (related_resource) {
                        if (!self.nodeIdMap[related_resource.entityid]) {
                            var node = {
                                id: self.newNodeId,
                                entityid: related_resource.entityid,
                                entitytypeid: related_resource.entitytypeid,
                                name: related_resource.primaryname,
                                relationType: 'Ancestor'
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
                                relationship: resource_relationships.preflabel.value,
                                weight: 1
                            });
                        }
                    });

                    callback({
                        nodes: nodes,
                        links: links
                    });
                }
            });
        }
    });
});

