define(['jquery', 'backbone', 'underscore', 'arches', 'd3'], function($, Backbone, _, arches) {
    return Backbone.View.extend({
        resourceId: null,
        resourceName: '',
        newNodeId: 0,
        nodeIdMap: {},

        initialize: function(options) {
            var self = this,
                data;

            _.extend(this, _.pick(options, 'resourceId', 'resourceName'));

            if (self.resourceId) {
                self.$el.addClass('loading');
                self.getResourceData(self.resourceId, this.resourceName, function (data) {
                    self.$el.removeClass('loading');
                    self.render(data);
                }, true);
            }
        },
        render: function (data) {
            var self = this,
                width = this.$el.parent().width(),
                height = 400;

            self.force = d3.layout.force()
                .charge(-750)
                .linkDistance(150)
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

            data.nodes[0].fixed = true;
            data.nodes[0].x = width/2;
            data.nodes[0].y = height/2;


            var canvasd3 = $(".arches-search-item-description"),
                aspect = canvasd3.width() / canvasd3.height(),
                containerd3 = canvasd3.parent();

            $(window).on("resize", function() {
                var targetWidth = containerd3.width();
                var targetHeight = containerd3.height();
                canvasd3.attr("width", targetWidth);
                canvasd3.attr("height", targetHeight);
            }).trigger("resize");


            data.nodes = self.force.nodes(data.nodes).nodes();
            data.links = self.force.links(data.links).links();

            self.update(data);

            self.$el.addClass('view-created');
        },

        update: function (data) {
            var self = this;
            var link = self.svg.selectAll(".link")
                .data(data.links);

            link.enter().insert("line", "circle")
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
                .data(data.nodes, function(d) { return d.id; });

            node.enter().append("circle")
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
                })
                .on("mouseover", function(){
                    d3.select(this).attr("class", function(d) {
                        if (d.relationType == "Current") {
                            return "node-current-over";
                        } else if (d.relationType == "Ancestor") {
                            return "node-ancestor-over";
                        } else {
                            return "node-descendent-over";
                        }
                    });
                })
                .on("mouseout", function(){
                    d3.select(this).attr("class", function(d) {
                        if (d.relationType == "Current") {
                            return "node-current";
                        } else if (d.relationType == "Ancestor") {
                            return "node-ancestor";
                        } else {
                            return "node-descendent";
                        }
                    });
                })
                .on("click", function (d) {
                    self.getResourceData(d.entityid, d.name, function (newData) {
                        texts.remove();
                        data.nodes = data.nodes.concat(newData.nodes);
                        data.links = data.links.concat(newData.links);
                        self.update(data);
                    }, false);
                })
                .call(self.force.drag);

            node.exit().remove();

            var texts = self.svg.selectAll("text.nodeLabels")
                .data(data.nodes);

            texts.enter().append("text")
                .attr("class", function(d){
                    if (d.relationType == "Current") {
                        return "node-current-label";
                    } else if (d.relationType == "Ancestor") {
                        return "node-ancestor-label";
                    } else {
                        return "node-descendent-label";
                    }
                })
                .attr("dy", ".35em")
                .text(function(d) {
                    return d.name;
                });

            texts.exit().remove();

            self.force.on("tick", function() {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });
         
                node
                    .attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; });
         
                texts
                    .attr("x", function(d) { return d.x; })
                    .attr("y", function(d) { return d.y; });
         
            });

            self.data = data;
            self.force.start();
        },

        getResourceData: function (resourceId, resourceName, callback, includeRoot) {
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
                                name: related_resource.primaryname,
                                relationType: 'Ancestor'
                            };
                            nodes.push(node);
                            self.nodeIdMap[related_resource.entityid] = node;
                            self.newNodeId += 1;
                        }
                    });

                    _.each(response.resource_relationships, function (resource_relationships) {
                        links.push({
                            source: self.nodeIdMap[resource_relationships.entityid1],
                            target: self.nodeIdMap[resource_relationships.entityid2],
                            relationship: resource_relationships.relationshiptype,
                            "weight": 1
                        });
                    });

                    console.log(nodes, links);

                    callback({
                        nodes: nodes,
                        links: links
                    });
                }
            });
        }
    });
});

