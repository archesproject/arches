define([
    'backbone',
    'views/graph/graph-manager/graph-base',
    'models/graph',
    'knockout',
    'd3'
], function(Backbone, GraphBase, GraphModel, ko, d3) {
    var GraphView = GraphBase.extend({
        /**
        * A backbone view to manage a list of branch graphs
        * @augments GraphBase
        * @constructor
        * @name GraphView
        */

        initialize: function(options) {
            this.graphModel = options.graphModel;
            this.selectedNode = options.graphModel.get('selectedNode');
            GraphBase.prototype.initialize.apply(this, arguments);
            
            options = _.defaults(options, {nodeSizeOver: this.nodeSize});
            this.nodeSizeOver = options.nodeSizeOver;

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

        /**
        * Renders only the nodes in the graph and adds Drag and Drop functionality 
        * as well as dynamically updating the styling based on hover events and allowing 
        * users to select a node by directly clicking it.  Nodes tagged as selected or filtered 
        * are rendered differently
        * @memberof GraphView.prototype
        */
        renderNodes: function(){
            GraphBase.prototype.renderNodes.apply(this, arguments);
            var self = this;
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
                        .attr("r", self.nodeSizeOver)
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
                        .attr("r", self.nodeSize)
                        .attr("class", function (d) {
                            return getNodeClass(d, '');
                        });
                });

            this.allNodes.exit()
                .remove();
        },

        /**
        * Renders the text associated with each node in the graph.  
        * Nodes tagged as filtered are rendered differently
        * @memberof GraphView.prototype
        */
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

        /**
        * Renders only the edges in the graph.  Nodes with a common group id have 
        * a different link styling
        * @memberof GraphView.prototype
        */
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

        /**
        * Listens to changes in node name or groupid and forces a {@link GraphView#render} 
        * @memberof GraphView.prototype
        */
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

        /**
        * Allows users to drag a part of the graph and append it to another part.  Styling 
        * of the graph is updated to reflect only valid drop targets.
        * @memberof GraphView.prototype
        */
        initDragDrop: function(){
            var self = this;
            var cache = {};
            var dragging = false;
            var draggingNode = null;

            var getTargetNodes = function(node, callback){
                if(_.has(cache, node.ontologyclass())){
                    callback(cache[node.ontologyclass()]);
                }else{
                    self.graphModel.getValidDomainClasses(node.nodeid, function(response){
                        cache[node.ontologyclass()] = response;
                        callback(response);
                    }, self);
                }
            };

            var testCanAppend = function(d, node, allowed_target_ontologies){
                var data = self.graphModel.getChildNodesAndEdges(d);
                data.nodes.push(d);
                data.nodes = _.map(data.nodes, function(node){
                    return node.toJSON();
                });
                data.ontology_id = self.graphModel.get('ontology_id');
                data.domain_connections = [{
                    ontology_classes: allowed_target_ontologies
                }]

                var draggedGraph = new GraphModel({
                    data: data
                });
   
                if(self.graphModel.canAppend(draggedGraph, node)){
                    return true;
                }

                return false;
            }

            var initiateDrag = function(d, draggedNodeElement) {
                var nodes = self.tree.nodes(d);
                draggingNode = d;

                getTargetNodes(d, function(response){
                    var allowed_target_ontologies = []
                    _.each(response, function(item){
                        allowed_target_ontologies = allowed_target_ontologies.concat(item.ontology_classes)
                    }, this)
                    allowed_target_ontologies = _.uniq(allowed_target_ontologies);
                    self.allNodes.property('canDrop', false);
                    nodes = self.allNodes.filter(function(node){
                        return testCanAppend(d, node, allowed_target_ontologies);
                    }, self);
                    nodes[0].forEach(function(node){
                        var d3node = d3.select(node);
                        if (d3node.data()[0].id != draggingNode.id){
                            d3node.attr('class', 'target-node')
                            .property('canDrop', true);
                        }
                    }, this);
                });

                

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
                self.graphModel.selectNode(draggingNode);
                draggingNode = null;
                dragging = false;
                self.loading(false);
            };

            // Define the drag listeners for drag/drop behaviour of nodes.
            this.dragListener = d3.behavior.drag()
                .on("dragstart", function(d) {
                    if (d.istopnode || d3.event.sourceEvent.shiftKey === false) {
                        return;
                    }
                    //console.log('drag start');
                    //dragStarted = true;
                    d3.event.sourceEvent.stopPropagation();
                    // it's important that we suppress the mouseover event on the node being dragged. 
                    // Otherwise it will absorb the mouseover event and the underlying node will not 
                    // detect it 
                    d3.select(this).attr('pointer-events', 'none');
                    initiateDrag(d, this);
                })
                .on("drag", function(d) {
                    if (d.istopnode || d3.event.sourceEvent.shiftKey === false) {
                        return;
                    }
                    //console.log('dragging');
                    dragging = true;

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
                        self.loading(true);
                        if (d3.event.sourceEvent.shiftKey === false || !self.overNode || self.overNode.property('canDrop') === false) {
                            endDrag();
                        }else{
                            self.graphModel.moveNode(draggingNode, 'P1', self.overNode.data()[0], function(){
                                endDrag();
                            }, self);
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
