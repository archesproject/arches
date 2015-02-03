define(['jquery', 'backbone', 'underscore', 'arches', 'resource-types', 'd3'], function($, Backbone, _, arches, resourceTypes) {
    var colorLuminance  = function(hex, lum) {
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
    }

    return Backbone.View.extend({
        resourceId: null,
        resourceName: '',
        resourceTypeId: '',
        newNodeId: 0,

        initialize: function(options) {
            var self = this;

            _.extend(this, _.pick(options, 'resourceId', 'resourceName', 'resourceTypeId'));
            this.nodeIdMap = {};
            this.linkMap = {};
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
                .attr("refX", 20)
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

            var link = self.svg.selectAll("line")
                .data(self.data.links);

            var linkEnter = link.enter().insert("line", "circle")
                .attr("class", "link")
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
                    self.svg.selectAll("circle").attr("class", function(d1){
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
                        var modifier = (d ===  d1) ? 0.7 : -0.3;
                        return "fill:" + resourceTypes[d1.entitytypeid].color + ";stroke:" + colorLuminance(resourceTypes[d1.entitytypeid].color, modifier);
                    });
                    self.svg.selectAll("line").attr('class', function(l) {
                        if (l.source === d || l.target === d) {
                            return 'linkMouseover';
                        } else {
                            return 'link';
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
                .on('mouseout', function (d) {
                    self.svg.selectAll("circle").attr("class", function(d1){
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
                    self.svg.selectAll("line").attr('class', function(l) {
                        return 'link';
                    });
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
                                relationship: sourceId.name + ' ' + resource_relationships.preflabel.value.split('/')[0] + targetId.name,
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
    });
});

