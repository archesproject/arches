define(['jquery', 'backbone', 'underscore', 'd3'], function($, Backbone, _) {
    return Backbone.View.extend({
        resourceId: null,

        initialize: function(options) {
            var self = this,
                data;

            _.extend(this, _.pick(options, 'resourceId'));

            if (self.resourceId) {
                self.$el.addClass('loading');
                self.getResourceData(self.resourceId, function (data) {
                    self.$el.removeClass('loading');
                    self.render(data);
                });
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


            var nodes = force.nodes(),
                links = force.links();
            
            //Load initial nodes/links
            nodes = data.nodes;

            links = data.links;


            //pin first node to center of svg
            nodes[0].fixed = true;
            nodes[0].x = width/2;
            nodes[0].y = height/2;


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


            // force
            //     .nodes(nodes)
            //     .links(links)
            //     .start();



            var update = function () {


                force
                .nodes(nodes)
                .links(links)
                .start();

                //Enter links, style as lines
                var link = svg.selectAll(".link")
                    .data(links)
                    .enter().insert("line", "circle")  //the "circle" makes sure that new links render under new nodes!
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


                //Enter nodes, style as circles
                var node = svg.selectAll("circle") 
                    .data(nodes, function(d) { return d.id; })
                    .enter().append("circle")
                    .attr("r",function(d){if(d.conceptType == "Current"){ return 24 } else if (d.conceptType == "Ancestor"){ return 18 }else { return 8 }})

                    .attr("r",function(d){if(d.conceptType == "Current"){ return currentNode } else if (d.conceptType == "Ancestor"){ return ancestorNode }else { return descendentNode }})

                    //.attr("class", "node")
                    .attr("class", function(d){if(d.conceptType == "Current"){ return "node-current"} else if (d.conceptType == "Ancestor"){ return "node-ancestor" } else { return "node-descendent" } })
                    
                    .on("mouseover", function(){

                        d3.select(this).attr("class", function(d) { 

                            if (d.conceptType == "Current") { return "node-current-over"} 
                            else if (d.conceptType == "Ancestor") { return "node-ancestor-over"} 
                            else { return "node-descendent-over"};

                        })

                    })

                    .on("mouseout", function(){

                        d3.select(this).attr("class", function(d) { 
                            
                            //Update node class
                            if (d.conceptType == "Current") { return "node-current"} 
                            else if (d.conceptType == "Ancestor") { return "node-ancestor"} 
                            else { return "node-descendent"};

         
                        })

                    })
                    

                    .on("click", function (d) {
                        d3.select(this)
                        var nodeName = d.id;
                        
                        //Use the node id to power a call to Arches to see if the clicked node has any related resources.
                        //If so, then push links/nodes for the new resource and then update graph
                        
                        //For now, just hard code new links/nodes
                        links.push(
                            {"source": 5, "target": 10, "relationship": "Built", "weight": 1}
                            
                        );


                        // Update nodes.
                        nodes.push({ id: "10", conceptName: "St Albans Church", conceptType: "Ancestor" });
                    
                        //Re-render graph with new nodes/links
                        update();

                    })

                    .call(force.drag);


                //Label Nodes
                var texts = svg.selectAll("text.nodeLabels")
                    .data(nodes)
                    .enter().append("text")
                    .attr("class", function(d){

                        if (d.conceptType == "Current") { return "node-current-label"} 
                        else if (d.conceptType == "Ancestor") { return "node-ancestor-label"} 
                        else { return "node-descendent-label"};

                    })

                    .attr("dy", ".35em")

                    .text(function(d) { return d.conceptName; }); 
                 

                // Label edges
                var labels = svg.selectAll('text.edgeLabels')
                    .data(links)
                    .enter().append('text')
                    .attr('class', 'edgeLabels')

                    //Label the edge.  Get the edge label from the target node
                    //.text(function(d) { return d.target.property; });  


                //Tooltip on nodes
                // node.append("title")
                //     .text(function(d) { return d.conceptType; });
             

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
             
                    labels
                        .attr("x", function(d) { return (d.source.x + d.target.x) / 2; }) 
                        .attr("y", function(d) { return (d.source.y + d.target.y) / 2; }) 
                    });


                // Restart the force layout.
                force.start();
            }

            // Make it all go
            update();


            self.$el.addClass('view-created');
        },
        getResourceData: function (resourceId, callback) {
            $.ajax({
                url: '../resources/get/' + resourceId,
                success: function(response) {

                    var links = [],
                        nodes = [{
                            id: 0,
                            entityid: response['_source'].entityid,
                            conceptName: response['_source'].primaryname,
                            conceptType: 'Current'
                        }],
                        nodeIdMap = {},
                        nodeId = 1;

                    nodeIdMap[response['_source'].entityid] = 0
                    _.each(response['_source'].related_resources, function (related_resources) {
                        nodes.push({
                            id: nodeId,
                            entityid: related_resources.entityid,
                            conceptName: related_resources.primaryname,
                            conceptType: 'Ancestor'
                        });
                        nodeIdMap[related_resources.entityid] = nodeId
                        nodeId += 1;
                    });

                    _.each(response['_source'].resource_relationships, function (resource_relationships) {
                        links.push({
                            source: nodeIdMap[resource_relationships.entityid1],
                            target: nodeIdMap[resource_relationships.entityid2],
                            relationship: resource_relationships.relationshiptype
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


    // "resource_relationships": [
    //   {
    //     "notes": "",
    //     "entityid2": "dea3ed16-13a2-438f-bf9c-9cd465ea3046",
    //     "entityid1": "6ea3e924-ecd4-432d-9c05-c93dab578899",
    //     "datestarted": null,
    //     "resourcexid": 2,
    //     "dateended": null,
    //     "relationshiptype": "ea1d6f73-24a5-4a7a-9491-347ed8a10d2f"
    //   },
    //   {
    //     "notes": "",
    //     "entityid2": "18688c0e-4950-4e67-a7b2-375d45b5822e",
    //     "entityid1": "6ea3e924-ecd4-432d-9c05-c93dab578899",
    //     "datestarted": null,
    //     "resourcexid": 3,
    //     "dateended": null,
    //     "relationshiptype": "17298183-5c74-4000-904c-bee6a95faaf8"
    //   },
    //   {
    //     "notes": "",
    //     "entityid2": "6ea3e924-ecd4-432d-9c05-c93dab578899",
    //     "entityid1": "a5de75a9-04c0-47a3-b929-3f74b387ff58",
    //     "datestarted": null,
    //     "resourcexid": 8,
    //     "dateended": null,
    //     "relationshiptype": "a100f1b1-59e7-4495-bc09-9aab31f81ae4"
    //   }
    // ],

    // "related_resources": [
    //   {
    //     "label": "",
    //     "primaryname": "Historic Resources Group",
    //     "value": "",
    //     "entitytypeid": "ACTOR.E39",
    //     "entityid": "dea3ed16-13a2-438f-bf9c-9cd465ea3046",
    //     "property": "",
    //     "businesstablename": ""
    //   },
    //   {
    //     "label": "",
    //     "primaryname": "SurveyLA: Sherman Oaks-Studio City-Toluca Lake-Cahuenga Pass Historic Resources Survey Report",
    //     "value": "",
    //     "entitytypeid": "INFORMATION_RESOURCE.E73",
    //     "entityid": "18688c0e-4950-4e67-a7b2-375d45b5822e",
    //     "property": "",
    //     "businesstablename": ""
    //   },
    //   {
    //     "label": "",
    //     "primaryname": "3264 N WRIGHTWOOD DR",
    //     "value": "",
    //     "entitytypeid": "HERITAGE_RESOURCE.E18",
    //     "entityid": "a5de75a9-04c0-47a3-b929-3f74b387ff58",
    //     "property": "",
    //     "businesstablename": ""
    //   }
    // ],