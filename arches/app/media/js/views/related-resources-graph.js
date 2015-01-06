define(['jquery', 'backbone', 'd3'], function($, Backbone) {
    return Backbone.View.extend({

        initialize: function() {
            var self = this;

            //Define basic SVG Container variables
            var panelWidth = $(".arches-search-item-description").width() - 50;

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
            nodes = [ 
                { id: "0", conceptName: "Castle Wolfenstein", conceptType: "Current" },
                { id: "1", conceptName: "Castle Anthrax", conceptType: "Ancestor" },
                { id: "2", conceptName: "Nunnery of Carol", conceptType: "Ancestor" },
                { id: "3", conceptName: "King Arthur", conceptType: "Ancestor" },
                { id: "4", conceptName: "Wolfenstein Aerial Image", conceptType: "Ancestor" },
                { id: "5", conceptName: "Earl of Crankcase", conceptType: "Ancestor" },
                { id: "6", conceptName: "Wolfenstein Investigation", conceptType: "Ancestor" },
                { id: "7", conceptName: "Bank of Kent", conceptType: "Ancestor" },
                { id: "8", conceptName: "Fencing Grounds", conceptType: "Ancestor" },
                { id: "9", conceptName: "Stables", conceptType: "Ancestor" },
            ];

            links = [   
                {"source":0, "target":1, "relationship": "Was at the location of"},
                {"source":0, "target":2, "relationship": "Is contained by"},
                {"source":0, "target":3, "relationship": "Was owned by"},
                {"source":0, "target":4, "relationship": "Describes"},
                {"source":0, "target":5, "relationship": "Architected"},
                {"source":0, "target":6, "relationship": "Describes"},
                {"source":5, "target":7, "relationship": "Founded"},
                {"source":1, "target":8, "relationship": "Contained"},
                {"source":1, "target":9, "relationship": "Contained"},
            ];


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
        }
    });
});