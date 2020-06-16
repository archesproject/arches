define(['arches'], function(arches) {
    var resourceLookup = {};
    var resourceUtils = {
        /**
         * lookupResourceInstanceData - gets resource instance data from Elastic Search
         *
         * @param  {resourceid} the id of the Resouce Instance
         * @return {object}
         */
        lookupResourceInstanceData: function(resourceid) {
            if (resourceLookup[resourceid]) {
                return Promise.resolve(resourceLookup[resourceid]);
            } else {
                return window.fetch(arches.urls.search_results + "?id=" + resourceid)
                    .then(function(response) {
                        if (response.ok) {
                            return response.json();
                        }
                    })
                    .then(function(json) {
                        resourceLookup[resourceid] = json["results"]["hits"]["hits"][0];
                        return resourceLookup[resourceid];
                    });
            }
        },

        /**
         * getNodeValues - gets resource instance data from Elastic Search
         *
         * @param  {queryClause} - object to specify which node to collect data from
         * also specifiying an optional "where" clause
         * the "where" clause specifies another node id within the same tile that 
         * needs meet the criteria specified in the "contains" parameter
         * 
         * if "returnTiles" is true, then it will return a list of tiles instead of node values
         *
         * the example below will return an array of values found in node id 
         * starting with "abcdefgh" where nodeid 
         * starting with "12345678" 
         * contains the value "0000000" (typically a concept valueid)
         *       {
         *           nodeId: 'abcdefgh-0000-0000-0000-000000000000',
         *           where: {
         *               nodeId: '12345678-0000-0000-0000-000000000000',
         *               contains: '0000000-0000-0000-0000-000000000000'
         *           },
         *           returnTiles: false
         *       };
         * 
         * you can also use "widgetLabel" instead of "nodeId" to resolve to a node id
         * 
         * if the "widgetLabel" is not unique then you can add an optional "Card Name" to
         * the widget labe in the form of "CardName.WidgetLabel" as in the example below
         * 
         *      {
         *           widgetLabel: 'In Collection or Set.member of',
         *           returnTiles: false
         *       }
         * 
         * 
         * @param  {tiles}
         * @param  {object} optional - only needed if using "widgetLabel" as part of the queryClause
         *  the object needs to specify a "cards" and "widgets" parameter eg: {cards: ..., widgets: ....}
         * @return {array of Tiles, or array of node values}
         */
        getNodeValues: function(queryClause, tiles, graph) {
            var nodeId;
            var foundTiles = [];
            var returnTiles = !!queryClause.returnTiles;

            var resolveWidgetLabel = function(cardWidgetPath, cards, widgets) {
                var cardName, cardids;
                var widgetLabel = '';
                var parts = cardWidgetPath.split('.');
                if (parts.length === 1) {
                    widgetLabel = parts[0];
                } else if (parts.length === 2) {
                    cardName = parts[0];
                    widgetLabel = parts[1];
                }

                if (!!cardName) {
                    cardids = cards.filter(function(card) {
                        return card.name === cardName;
                    }).map(function(card) {
                        return card.cardid;
                    });

                    widgets = widgets.filter(function(widget) {
                        return cardids.includes(widget.card_id);
                    });
                }

                var nodeId = widgets.filter(function(widget) {
                    return widget.label === widgetLabel;
                }).map(function(widget) {
                    return widget.node_id;
                });

                if (!nodeId || nodeId.length > 1) {
                    console.log('Can\'t resolve path \'', cardWidgetPath, '\' into a single nodeid');
                }
                return nodeId;
            };

            if (!!queryClause.nodeId) {
                nodeId = [queryClause.nodeId];
            } else if (!!queryClause.nodeName) {
                var node = graph.nodes.find(function(node) {
                    return node.name === queryClause.nodeName;
                });
                if (!!node) {
                    nodeId = node.nodeid;
                }
            } else if (!!queryClause.widgetLabel) {
                nodeId = resolveWidgetLabel(queryClause.widgetLabel, graph.cards, graph.widgets);
            }

            if (!!nodeId && nodeId.length === 1) {
                nodeId = nodeId[0];
                foundTiles = tiles.filter(function(tile) {
                    return Object.keys(tile.data).includes(nodeId);
                });
                if (!!queryClause.where) {
                    if (!!queryClause.where.nodeId) {
                        foundTiles = foundTiles.filter(function(tile) {
                            if (!!queryClause.where.contains) {
                                return tile.data[queryClause.where.nodeId].includes(queryClause.where.contains);
                            }
                            return false;
                        });
                    } else if (!!queryClause.where.widgetLabel) {
                        var whereNodeId = resolveWidgetLabel(queryClause.where.widgetLabel, graph.cards, graph.widgets);
                        if (!!whereNodeId && whereNodeId.length === 1) {
                            foundTiles = foundTiles.filter(function(tile) {
                                if (!!queryClause.where.contains) {
                                    return tile.data[whereNodeId].includes(queryClause.where.contains);
                                }
                                return false;
                            });
                        }
                    }
                }

                if (returnTiles) {
                    return foundTiles;
                } else {
                    return foundTiles.map(function name(tile) {
                        return tile.data[nodeId];
                    }).flat(Infinity);
                }
            }
            return undefined;
        }
    };
    return resourceUtils;
});