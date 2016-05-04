define([
    'backbone',
    'views/graph-manager/graph-base',
    'knockout',
    'd3'
], function(Backbone, GraphBase, ko, d3) {
    var GraphView = GraphBase.extend({
        initialize: function(options) {
            this.graphModel = options.graphModel;
            this.selectedNode = options.graphModel.get('selectedNode');
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
                this.selectedNode();
                this.render();
            }, this);
        },
        renderNodes: function(){
            GraphBase.prototype.renderNodes.apply(this, arguments);
            var self = this;
            var nodeMouseOver = 8;
            var getNodeClass = function (d, className) {
                className += d.selected() ? ' node-selected' : '';
                className += d.filtered() ? ' node-filtered' : '';
                className += (self.selectedNode() && self.selectedNode().nodeGroupId() === d.nodeGroupId()) ? ' node-collected' : '';
                return className;
            }
            this.initDragDrop();
            this.allNodes.selectAll('circle')
                .call(this.dragListener)
                .attr("class", function (d) {
                    return getNodeClass(d, '');
                })
                .on("mouseover", function(d) {
                    self.overNode = d3.select(this.parentElement);
                    d3.select(this)
                        .attr("r", nodeMouseOver)
                        .attr("class", function (d) {
                            return getNodeClass(d, 'node-over');
                        })
                })
                .on("click", function (node) {
                    self.graphModel.selectNode(node);
                })
                .on("mouseout", function(d) {
                    self.overNode = null;
                    d3.select(this)
                        .attr("r", self.nodesize)
                        .attr("class", function (d) {
                            return getNodeClass(d, '');
                        });
                });

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
                    if (self.selectedNode()) {
                        var selectedGroup = self.selectedNode().nodeGroupId();
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
            var dragging = false;
            var draggingNode = null;

            var getTargetNodes = function(ontologyclass){
                var allowed_target_ontologies = ['E1', 'E2'];
                self.allNodes.property('canDrop', false);
                return self.allNodes.filter(function(node){
                    return _.indexOf(allowed_target_ontologies, node.ontologyclass) !== -1
                }, self);
            };

            var initiateDrag = function(d, draggedNodeElement) {
                var nodes = self.tree.nodes(d);
                draggingNode = d;

                // style possible drop targets
                getTargetNodes(d.ontologyclass)[0].forEach(function(node){
                    var d3node = d3.select(node);
                    if (d3node.data()[0].id != draggingNode.id){
                        d3node.attr('class', 'target-node')
                        .property('canDrop', true);
                    }
                }, this);

                // remove the text of the dragged node
                draggedNodeElement.nextSibling.remove();

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

            var endDrag = function() {
                self.redraw(true);
                draggingNode = null;
                dragging = false;
            };

            // Define the drag listeners for drag/drop behaviour of nodes.
            this.dragListener = d3.behavior.drag()
                .on("dragstart", function(d) {
                    if (d.istopnode || d3.event.sourceEvent.shiftKey === false) {
                        return;
                    }
                    //console.log('drag start');
                    dragStarted = true;
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
                    //console.log('dragging');
                    if (dragStarted) {
                        dragging = true;
                        initiateDrag(d, this);
                    }

                    if (isNaN(d.x)) {
                        d.x = 0;
                    }

                    var mouse_location = d3.mouse(self.svg[0][0]);
                    var node = d3.select(this);
                    d.x = mouse_location[1];
                    d.y = mouse_location[0] / 180 * Math.PI;
                    node.attr("transform", "translate(" + d3.event.x + "," + d3.event.y + ")");
                    //updateTempConnector();
                }).on("dragend", function(d) {
                    //console.log('drag end');
                    if (dragging){
                        if (d3.event.sourceEvent.shiftKey === false || !self.selectedNode || self.selectedNode.property('canDrop') === false) {
                            endDrag();
                            return;
                        }else{
                            self.graphModel.moveNode(draggingNode, 'P1', self.selectedNode.data()[0], function(){
                            }, self);
                            endDrag();
                        }
                    }
                });


            // Function to update the temporary connector indicating dragging affiliation
            var updateTempConnector = function() {
                var dist = null;
                var closestNode = null;
                self.allNodes[0].forEach(function(node){
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
                }, self);
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

                var link = self.svg.selectAll(".templink").data(data);

                link.enter().append("path")
                    .attr("class", "templink")
                    .attr("d", self.diagonal)
                    .attr('pointer-events', 'none');

                link.attr("d", self.diagonal);

                link.exit().remove();
            };
        }
    });
    return GraphView;
});
