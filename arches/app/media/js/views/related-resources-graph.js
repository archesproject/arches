define(['jquery', 'backbone', 'underscore', 'd3'], function($, Backbone, _) {
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
            var self = this;

            //Define basic SVG Container variables
            var panelWidth = this.$el.parent().width();

            var width = panelWidth,  //800,
                height = 400,
                nodesize = 12;  //Default node size
                nodeMouseOver = 14; //Mouseover Node size
                opacity = 0.5;



            //Set up node sizes
            var currentNode = 30,  
                ancestorNode = 22,
                descendentNode = 16,
                selectSize = 4;



            //Set up D3 Force Directed Graph as the visualization, define basic parameters
            var force = d3.layout.force()
                .charge(-750)
                .linkDistance(150)
                .gravity(0.05)
                .friction(.55)
                .linkStrength(function(l, i) {return 1; })  
                .theta(.8)
                .size([width, height]);
             

            //Set up color palette to make styling nodes easier
            var color = d3.scale.category20();


            //Setup SVG container for the Graph Visualization, Set up Zoom support
            //Define  an SVG group to hold the nodes/links in the visualization
            var svg = d3.select(this.el).append("svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", redraw))
                .append('svg:g');

                //Zoom support: Redraw Graph on zoom
                function redraw() {
                    //console.log("here", d3.event.translate, d3.event.scale);
                    svg.attr("transform",
                        "translate(" + d3.event.translate + ")"
                        + " scale(" + d3.event.scale + ")");
                }

            //pin first node to center of svg
            data.nodes[0].fixed = true;
            data.nodes[0].x = width/2;
            data.nodes[0].y = height/2;


            var canvasd3 = $(".arches-search-item-description"),
                aspect = canvasd3.width() / canvasd3.height(),
                containerd3 = canvasd3.parent();


            //Manage D3 graph on resize of window
            $(window).on("resize", function() {
                var targetWidth = containerd3.width();
                var targetHeight = containerd3.height();
                canvasd3.attr("width", targetWidth);
                canvasd3.attr("height", targetHeight);

                    //Start the simulation
                    // force
                    //     .nodes(data.nodes)
                    //     .links(data.links)
                    //     .start();

                }).trigger("resize");


            data.nodes = force.nodes(data.nodes).nodes();
            data.links = force.links(data.links).links();

            var findNode = function (id) {
                for (var i=0; i < data.nodes.length; i++) {
                    if (data.nodes[i].id === id)
                        return data.nodes[i]
                };
            }

            var update = function () {

                //Enter links, style as lines
                var link = svg.selectAll(".link")
                    .data(data.links);

                link.enter().insert("line", "circle")  //the "circle" makes sure that new links render under new nodes!
                    .attr("class", "link")

                    //add interactivity
                    .on("mouseover", function(d) {
                        d3.select(this)
                        .attr("class", "linkMouseover")

                        //add tooltup to show edge property
                        link.append("title")
                        .text(function(d) { return d.relationship; })

                    })

                    .on("mouseout", function(d) {
                        d3.select(this)
                        .attr("class", "link");
                    })

                link.exit().remove();


                //Enter nodes, style as circles
                var node = svg.selectAll("circle") 
                    .data(data.nodes, function(d) { return d.id; });

                node.enter().append("circle")
                    .attr("r",function(d){if(d.relationType == "Current"){ return 24 } else if (d.relationType == "Ancestor"){ return 18 }else { return 8 }})

                    .attr("r",function(d){if(d.relationType == "Current"){ return currentNode } else if (d.relationType == "Ancestor"){ return ancestorNode }else { return descendentNode }})

                    //.attr("class", "node")
                    .attr("class", function(d){if(d.relationType == "Current"){ return "node-current"} else if (d.relationType == "Ancestor"){ return "node-ancestor" } else { return "node-descendent" } })
                    
                    .on("mouseover", function(){

                        d3.select(this).attr("class", function(d) { 

                            if (d.relationType == "Current") { return "node-current-over"} 
                            else if (d.relationType == "Ancestor") { return "node-ancestor-over"} 
                            else { return "node-descendent-over"};

                        })

                    })

                    .on("mouseout", function(){

                        d3.select(this).attr("class", function(d) { 
                            
                            //Update node class
                            if (d.relationType == "Current") { return "node-current"} 
                            else if (d.relationType == "Ancestor") { return "node-ancestor"} 
                            else { return "node-descendent"};

         
                        })

                    })
                    

                    .on("click", function (d) {
                        self.getResourceData(d.entityid, d.name, function (newData) {
                            texts.remove();
                            data.nodes = data.nodes.concat(newData.nodes);
                            data.links = data.links.concat(newData.links);
                            update();
                        }, false);
                    })

                    .call(force.drag);

                node.exit().remove();


                //Label Nodes
                var texts = svg.selectAll("text.nodeLabels")
                    .data(data.nodes)
                    .enter().append("text")
                    .attr("class", function(d){

                        if (d.relationType == "Current") { return "node-current-label"} 
                        else if (d.relationType == "Ancestor") { return "node-ancestor-label"} 
                        else { return "node-descendent-label"};

                    })

                    .attr("dy", ".35em")

                    .text(function(d) { return d.name; }); 
                 

                    //Label the edge.  Get the edge label from the target node
                    //.text(function(d) { return d.target.property; });  


                //Tooltip on nodes
                // node.append("title")
                //     .text(function(d) { return d.relationType; });

             

                force.on("tick", function() {
                    link
                        .attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });
             
                    node
                        .attr("cx", function(d) { return d.x; })
                        .attr("cy", function(d) { return d.y; });
             
                    texts
                        //.attr("x", function(d) { console.log(d); return d.x + 15; })
                        .attr("x", function(d) { return d.x; })
                        .attr("y", function(d) { return d.y; })
             
                    });


                // Restart the force layout.
                self.data = data;
                force.start();
            }

            // Make it all go
            update();


            self.$el.addClass('view-created');
        },
        getResourceData: function (resourceId, resourceName, callback, includeRoot) {
            var self = this;
            $.ajax({
                url: '../resources/get/' + resourceId,
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
                        })
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

