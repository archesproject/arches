define([
    'backbone',
    'views/graph-manager/graph-base',
    'knockout',
    'd3'
], function(Backbone, GraphBase, ko, d3) {
    var GraphView = GraphBase.extend({
        initialize: function(options) {
            this.editNode = options.graphModel.get('editNode');
            this.selectedNodes = options.graphModel.get('selectedNodes');
            GraphBase.prototype.initialize.apply(this, arguments);

            this.addNodeListeners();
            this.nodes.subscribe(function() {
                this.render();
                this.addNodeListeners();
            }, this);
            this.edges.subscribe(function() {
                this.render();
            }, this);

            ko.computed(function() {
                this.editNode();
                this.selectedNodes();
                this.render();
            }, this);
        },
        renderNodes: function(){
            GraphBase.prototype.renderNodes.apply(this, arguments);
            var self = this;
            var nodeMouseOver = 8;
            var getNodeClass = function (d, className) {
                className += d.editing() ? ' node-editing' : '';
                className += d.selected() ? ' node-selected' : '';
                className += d.filtered() ? ' node-filtered' : '';
                className += (self.editNode() && self.editNode().nodeGroupId() === d.nodeGroupId()) ? ' node-collected' : '';
                return className;
            }
            this.initDragDrop();
            this.allNodes.selectAll('circle')
                .call(this.dragListener)
                .attr("class", function (d) {
                    return getNodeClass(d, '');
                })
                .on("mouseover", function(d) {
                    self.selectedNode = d3.select(this.parentElement);
                    d3.select(this)
                        .attr("r", nodeMouseOver)
                        .attr("class", function (d) {
                            return getNodeClass(d, 'node-over');
                        })
                })
                .on("click", function (node) {
                    self.trigger('node-clicked', node);
                })
                .on("mouseout", function(d) {
                    self.selectedNode = null;
                    d3.select(this)
                        .attr("r", self.nodesize)
                        .attr("class", function (d) {
                            return getNodeClass(d, '');
                        });
                });

            // this.allNodes           
            //     // phantom node to give us mouseover in a radius around it
            //     .append("circle")
            //     .attr('class', 'ghostCircle')
            //     .attr("r", 30)
            //     .attr("opacity", 0.2) // change this to zero to hide the target area
            //     .style("fill", "red")
                // .attr('pointer-events', 'mouseover')
                // .on("mouseover", function(node) {
                //     overCircle(node);
                // })
                // .on("mouseout", function(node) {
                //     outCircle(node);
                // })

            this.allNodes.exit()
                .remove();
        },
        renderNodeText: function(){
            GraphBase.prototype.renderNodeText.apply(this, arguments);
            var getNodeClass = function (d, className) {
                className += d.filtered() ? ' node-filtered' : '';
                return className;
            }
            this.allNodes.selectAll('text')
                .attr("class", function (d) {
                    return getNodeClass(d, '');
                })
        },
        renderLinks: function(){
            var self = this;
            GraphBase.prototype.renderLinks.apply(this, arguments);
            this.svg.selectAll(".link")
                .attr("class", function (d) {
                    var className = 'link';
                    if (self.editNode()) {
                        var selectedGroup = self.editNode().nodeGroupId();
                        if (d.source.nodeGroupId() === selectedGroup && d.target.nodeGroupId() === selectedGroup) {
                            className += ' link-collected';
                        }
                    }
                    return className;
                });
        },
        addNodeListeners: function () {
            var self = this;
            var nodes = this.nodes();

            nodes.forEach(function (node) {
                node.name.subscribe(function () {
                    self.render();
                });
                node.nodeGroupId.subscribe(function () {
                    self.render();
                });
            });
        },
        initDragDrop: function(){
            var self = this;
            var initiateDrag = function(d, draggedNode) {
                draggingNode = d;
                // d3.select(draggedNode).select('.ghostCircle').attr('pointer-events', 'none');
                // d3.selectAll('.ghostCircle').attr('class', 'ghostCircle show');
                // d3.select(draggedNode).attr('class', 'node activeDrag');
                self.allNodes.sort(function(a, b) {
                    // select the parent and sort the path's 
                    if (a.id != draggingNode.id) return 1;
                    // a is not the hovered element, send "a" to the back else return -1; 
                    // a is the hovered element, bring "a" to the front 
                }); 

                self.getTargetNodes(d.ontologyclass)[0].forEach(function(node){
                    d3.select(node)
                    .attr('class', 'target-node')
                    .property('canDrop', true);
                }, this);

                // remove the text of the dragged node
                draggedNode.nextSibling.remove();

                //if nodes has children, remove the links and nodes 
                if (nodes.length > 1) {

                    // remove link paths
                    links = self.tree.links(nodes);

                    nodePaths = self.svg.selectAll("path.link")
                        .data(links, function(d) {
                            return d.target.id;
                        }).remove();

                    // remove child nodes
                    nodesExit = self.allNodes
                        .data(nodes, function(d) {
                            return d.id;
                        }).filter(function(d, i) {
                            if (d.id == draggingNode.id) {
                                return false;
                            }
                            return true;
                        }).remove();
                }

                self.svg.selectAll('path.link').filter(function(d, i) {
                    if (d.target.id == draggingNode.id) {
                        return true;
                    }
                    return false;
                }).remove();

                dragStarted = null;
            }
            // Define the drag listeners for drag/drop behaviour of nodes.
            this.dragListener = d3.behavior.drag()
                .on("dragstart", function(d) {
                    if (d.istopnode || d3.event.sourceEvent.shiftKey === false) {
                        return;
                    }
                    console.log('drag start');
                    dragStarted = true;
                    nodes = self.tree.nodes(d);
                    d3.event.sourceEvent.stopPropagation();
                    // it's important that we suppress the mouseover event on the node being dragged. 
                    // Otherwise it will absorb the mouseover event and the underlying node will not 
                    // detect it 
                    d3.select(this).attr('pointer-events', 'none');
                })
                .on("drag", function(d) {
                    if (d.istopnode || d3.event.sourceEvent.shiftKey === false) {
                        return;
                    }
                    console.log('dragging');
                    if (dragStarted) {
                        draggedNode = this;
                        initiateDrag(d, draggedNode);
                    }

                    // // get coords of mouseEvent relative to svg container to allow for panning
                    // relCoords = d3.mouse($('svg').get(0));
                    // if (relCoords[0] < panBoundary) {
                    //     panTimer = true;
                    //     pan(this, 'left');
                    // } else if (relCoords[0] >
                    //     ($('svg').width() - panBoundary)) {

                    //     panTimer = true;
                    //     pan(this, 'right');
                    // } else if (relCoords[1] < panBoundary) {
                    //     panTimer = true;
                    //     pan(this, 'up');
                    // } else if (relCoords[1] >
                    //     ($('svg').height() - panBoundary)) {
                    //     panTimer = true;
                    //     pan(this, 'down');
                    // } else {
                    //     try {
                    //         clearTimeout(panTimer);
                    //     } catch (e) {

                    //     }
                    // }
                    console.log(d3.mouse(self.svg[0][0]))
                    //console.log(d3.event.dx + "," + d3.event.dy)
                    if (isNaN(d.x)) {
                        d.x = 0;
                    }

                    // d.x += d3.event.dx;
                    // d.y += d3.event.dy;
                    var mouse_location = d3.mouse(self.svg[0][0]);
                    d.x = mouse_location[1];
                    d.y = mouse_location[0] / 180 * Math.PI;
                    var node = d3.select(this);
                    node.attr("transform", "translate(" + d3.event.x + "," + d3.event.y + ")");
                    self.updateTempConnector();
                }).on("dragend", function(d) {
                    if (d3.event.sourceEvent.shiftKey === false || !self.selectedNode || self.selectedNode.property('canDrop') === false) {
                        self.endDrag();
                        return;
                    }else{
                        console.log('drag end');
                        draggedNode = this;
                        self.graphModel.moveNode(draggingNode, 'P1', self.selectedNode.data()[0], function(){
                        }, self);
                        self.endDrag();
                    }
                });

            this.endDrag = function() {
                this.selectedNode = null;
                d3.selectAll('.ghostCircle').attr('class', 'ghostCircle');
                d3.select(draggedNode).attr('class', 'node');
                // now restore the mouseover event or we won't be able to drag a 2nd time
                d3.select(draggedNode).select('.ghostCircle').attr('pointer-events', '');
                //updateTempConnector();
                if (draggingNode !== null) {
                    //update(root);
                    //centerNode(draggingNode);
                    this.redraw(true);
                    draggingNode = null;
                }
            }

            this.getTargetNodes = function(ontologyclass){
                var allowed_target_ontologies = ['E1', 'E2'];
                this.allNodes.property('canDrop', false);
                return this.allNodes.filter(function(node){
                    return _.indexOf(allowed_target_ontologies, node.ontologyclass) !== -1
                }, this);
            },

            // Function to update the temporary connector indicating dragging affiliation
            this.updateTempConnector = function() {
                var dist = null;
                var closestNode = null;
                this.allNodes[0].forEach(function(node){
                    var thisnode = d3.select(node).data()[0];
                    if(thisnode !== draggingNode){
                        var nodedist = Math.sqrt(Math.pow(thisnode.x-draggingNode.x,2) + Math.pow(thisnode.y-draggingNode.y,2));
                        if (dist === null){
                            dist = nodedist;
                            closestNode = thisnode;
                        }else{
                            if(nodedist < dist){
                                dist = nodedist;
                                closestNode = thisnode;
                            }
                        }
                    }
                }, this);
                var data = [];
                //if (draggingNode !== null && closestNode !== null) {
                     data = [{
                        target: {
                            x: closestNode.x,
                            y: closestNode.y
                        },
                        source: {
                            x: draggingNode.x,
                            y: draggingNode.y
                        }
                    }];
                //}

                //return [d.y, d.x / 180 * Math.PI]
                //console.log(data[0].source)

                var link = this.svg.selectAll(".templink").data(data);

                link.enter().append("path")
                    .attr("class", "templink")
                    .attr("d", this.diagonal)
                    .attr('pointer-events', 'none');

                link.attr("d", this.diagonal);

                link.exit().remove();
            };
        }
    });
    return GraphView;
});
