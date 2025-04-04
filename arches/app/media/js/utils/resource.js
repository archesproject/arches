import arches from 'arches';

const resourceUtils = {
    /**
     * lookupResourceInstanceData - gets resource instance data from Elastic Search
     *
     * @param  {resourceid} the id of the Resource Instance
     * @return {object}
     */
    lookupResourceInstanceData: function(resourceid, resourceLookup, usecache=true) {
        if (resourceLookup[resourceid] && usecache) {
            return Promise.resolve(resourceLookup[resourceid]);
        } else {
            return window.fetch(`${arches.urls.search_results}?id=${resourceid}&tiles=true`)
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
     * lookupResourceInstanceDataByQuery - gets resource instance(s) from Elasticsearch using custom query
     *
     * @param  {query} a premade ES query
     * @return {array}
     */
    lookupResourceInstanceDataByQuery: function(query) {
        const searchParams = new URLSearchParams({
            'advanced-search': JSON.stringify([query]),
            tiles: true
        });
        return window.fetch(`${arches.urls.search_results}?${searchParams}`)
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                }
            })
            .then(function(json) {
                return json["results"]["hits"]["hits"];
            });
    },

    /**
     * getNodeValues - gets resource instance data from Elastic Search
     *
     * @param  {queryClause} - object to specify which node to collect data from
     * also specifying an optional "where" clause
     * the "where" clause specifies another node id within the same tile that 
     * needs to meet the criteria specified in the "contains" parameter
     * 
     * if "returnTiles" is true, then it will return a list of tiles instead of node values
     *
     * @param  {tiles}
     * @param  {object} optional - only needed if using "widgetLabel" as part of the queryClause
     *  the object needs to specify a "cards" and "widgets" parameter eg: {cards: ..., widgets: ....}
     * @return {array of Tiles, or array of node values}
     */
    getNodeValues: function(queryClause, tiles, graph) {
        let nodeId;
        let foundTiles = [];
        const returnTiles = !!queryClause.returnTiles;

        const resolveWidgetLabel = function(cardWidgetPath, cards, widgets) {
            let cardName, cardids;
            let widgetLabel = '';
            const parts = cardWidgetPath.split('.');
            if (parts.length === 1) {
                widgetLabel = parts[0];
            } else if (parts.length === 2) {
                cardName = parts[0];
                widgetLabel = parts[1];
            }

            if (cardName) {
                cardids = cards.filter(function(card) {
                    return card.name === cardName;
                }).map(function(card) {
                    return card.cardid;
                });

                widgets = widgets.filter(function(widget) {
                    return cardids.includes(widget.card_id);
                });
            }

            const nodeId = widgets.filter(function(widget) {
                return widget.label === widgetLabel;
            }).map(function(widget) {
                return widget.node_id;
            });

            if (!nodeId || nodeId.length > 1) {
                console.log('Can\'t resolve path \'', cardWidgetPath, '\' into a single nodeid');
            }
            return nodeId;
        };

        if (queryClause.nodeId) {
            nodeId = [queryClause.nodeId];
        } else if (queryClause.nodeName) {
            const node = graph.nodes.find(function(node) {
                return node.name === queryClause.nodeName;
            });
            if (node) {
                nodeId = node.nodeid;
            }
        } else if (queryClause.widgetLabel) {
            nodeId = resolveWidgetLabel(queryClause.widgetLabel, graph.cards, graph.widgets);
        }

        if (nodeId && nodeId.length === 1) {
            nodeId = nodeId[0];
            foundTiles = tiles.filter(function(tile) {
                return Object.keys(tile.data).includes(nodeId);
            });
            if (queryClause.where) {
                if (queryClause.where.nodeId) {
                    foundTiles = foundTiles.filter(function(tile) {
                        if (queryClause.where.contains) {
                            return tile.data[queryClause.where.nodeId].includes(queryClause.where.contains);
                        }
                        return false;
                    });
                } else if (queryClause.where.widgetLabel) {
                    const whereNodeId = resolveWidgetLabel(queryClause.where.widgetLabel, graph.cards, graph.widgets);
                    if (whereNodeId && whereNodeId.length === 1) {
                        foundTiles = foundTiles.filter(function(tile) {
                            if (queryClause.where.contains) {
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

export default resourceUtils;
