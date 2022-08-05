define([
    'jquery',
    'underscore',
    'knockout',
    'viewmodels/card',
    'models/card-widget',
    'arches',
    'uuid',
    'graph-designer-data',
    'bindings/sortable',
    'bindings/scrollTo',
    'widgets',
    'card-components'
], function($, _, ko, CardViewModel, CardWidgetModel, arches, uuid, data) {
    var CardTreeViewModel = function(params) {
        var self = this;
        var filter = ko.observable('');
        var loading = ko.observable(false);
        self.multiselect = params.multiselect || false;
        var selection;
        if (params.multiselect) {
            selection = ko.observableArray([]);
        } else {
            selection = ko.observable();
        }
        var hover = ko.observable();
        var scrollTo = ko.observable();
        var cachedFlatTree;
        var cardList = data.cards;

        var getBlankConstraint = function(card){
            return [{
                uniquetoallinstances: false,
                nodes: [],
                cardid: card.cardid,
                constraintid: uuid.generate()
            }];
        };

        this.flattenTree = function(parents, flatList) {
            _.each(ko.unwrap(parents), function(parent) {
                flatList.push(parent);
                self.flattenTree(
                    ko.unwrap(parent.cards),
                    flatList
                );
            }, this);
            return flatList;
        };

        this.updateNodeList = function() {
            if (self.cachedFlatTree === undefined) {
                self.cachedFlatTree = self.flattenTree(self.topCards(), []);
            }
        };

        var toggleAll = function(state) {
            self.updateNodeList();
            _.each(self.cachedFlatTree, function(node) {
                node.expanded(state);
            });
            if (state) {
                self.rootExpanded(true);
            }
        };

        var selectAll = function(state) {
            self.updateNodeList();
            _.each(self.cachedFlatTree, function(node) {
                if (node.selected() !== state) {
                    node.selected(state);
                }
            });
        };

        var expandToRoot = function(node) {
            //expands all nodes up to the root, but does not expand the root.
            self.updateNodeList();
            if (node.parent) {
                node.parent.expanded(true);
                expandToRoot(node.parent);
            } else {
                node.expanded(true);
                _.each(self.cachedFlatTree, function(n) {
                    if (node.parentnodegroup_id !== null && node.parentnodegroup_id === n.nodegroupid) {
                        expandToRoot(n);
                    }
                });
            }
        };

        var removeCard = function(cards, nodegroupid) {
            var removed;
            _.each(cards(), function(card){
                if (card) {
                    if (card.nodegroupid === nodegroupid) {
                        cards.remove(card);
                        removed = card;
                    } else {
                        removeCard(card.cards, nodegroupid);
                    }
                }
            });
            return removed;
        };

        var createLookup = function(list, idKey) {
            return _.reduce(list, function(lookup, item) {
                lookup[ko.unwrap(item[idKey])] = item;
                return lookup;
            }, {});
        };

        _.extend(this, {
            filterEnterKeyHandler: function(context, e) {
                if (e.keyCode === 13) {
                    var highlightedItems = _.filter(self.flattenTree(self.topCards(), []), function(item) {
                        return item.highlight && item.highlight();
                    });
                    var previousItem = scrollTo();
                    scrollTo(null);
                    if (highlightedItems.length > 0) {
                        var scrollIndex = 0;
                        var previousIndex = highlightedItems.indexOf(previousItem);
                        if (previousItem && highlightedItems[previousIndex+1]) {
                            scrollIndex = previousIndex + 1;
                        }
                        scrollTo(highlightedItems[scrollIndex]);
                    }
                    return false;
                }
                return true;
            },
            loading: loading,
            showIds: ko.observable(false),
            cachedFlatTree: cachedFlatTree,
            widgetLookup: createLookup(data.widgets, 'widgetid'),
            cardComponentLookup: createLookup(data.cardComponents, 'componentid'),
            nodeLookup: createLookup(params.graphModel.get('nodes')(), 'nodeid'),
            graphid: params.graph.graphid,
            graphname: params.graph.name,
            graphiconclass: params.graph.iconclass,
            graph: params.graph,
            graphModel: params.graphModel,
            appliedFunctions: params.appliedFunctions(),
            primaryDescriptorFunction: params.primaryDescriptorFunction(),
            toggleIds: function() {
                self.showIds(!self.showIds());
            },
            expandAll: function() {
                toggleAll(true);
            },
            collapseAll: function() {
                toggleAll(false);
            },
            selectAllCards: function() {
                selectAll(true);
            },
            clearSelection: function() {
                selectAll(false);
            },
            expandToRoot: expandToRoot,
            rootExpanded: ko.observable(true),
            on: function() {
                return;
            },
            beforeMove: function(e) {
                e.cancelDrop = (e.sourceParent!==e.targetParent);
            },
            updateCard: function(parents, card, data) {
                var updatedCards = [];
                _.each(ko.unwrap(parents), function(parent) {
                    if (parent.nodegroupid === card.parentnodegroupId) {
                        var newcard = {
                            card: card,
                            nodegroup: _.filter(data.nodegroups, function(ng){return data.updated_values.card.nodegroup_id === ng.nodegroupid;})[0]
                        };
                        self.addCard(newcard, parent.cards, parent);
                    } else {
                        self.updateCard(ko.unwrap(parent.cards), card, data);
                    }
                }, this);
                return updatedCards;
            },
            updateNode: function(parents, node) {
                var updatedCards = [];
                if (_.contains(_.keys(self.nodeLookup), node.nodeid) === false) {
                    self.nodeLookup[node.nodeid] = node;
                }
                _.each(ko.unwrap(parents), function(parent) {
                    if (parent.nodegroupid === node.nodegroup_id) {
                        var attributes = parent.model.attributes;
                        _.each(parent.model.nodes(), function(modelnode){
                            if (modelnode.nodeid === node.nodeid) {
                                var datatype = attributes.datatypelookup[ko.unwrap(modelnode.datatype)];
                                if (!modelnode.nodeDatatypeSubscription) {
                                    modelnode.nodeDatatypeSubscription = modelnode.datatype.subscribe(function(){
                                        parent.model._card(JSON.stringify(parent.model.toJSON()));
                                    }, this);
                                }
                                if (datatype.defaultwidget_id) {
                                    var cardWidgetData = _.find(attributes.data.widgets, function(widget) {
                                        return widget.node_id === node.nodeid;
                                    });
                                    var widget = new CardWidgetModel(cardWidgetData, {
                                        node: modelnode,
                                        card: parent.model,
                                        datatype: datatype,
                                        disabled: attributes.data.disabled
                                    });
                                    var widgetIndex;
                                    _.each(parent.widgets(), function(pw, i){
                                        if (pw.node_id() === widget.node_id()) {
                                            widgetIndex = i;
                                        }
                                    }, self);
                                    if (widgetIndex !== undefined) {
                                        parent.widgets.splice(widgetIndex, 1, widget);
                                    } else {
                                        parent.widgets.push(widget);
                                    }
                                }
                            }
                        });
                        parent.model._card(JSON.stringify(parent.model.toJSON()));
                    } else {
                        self.updateNode(ko.unwrap(parent.cards), node);
                    }
                }, this);
                return updatedCards;
            },
            updateCards: function(selectedNodegroupId, data) {
                self.updateNode(self.topCards(), data.updated_values.node);

                if (data.updated_values.card) {
                    var card = data.updated_values.card;
                    var defaultCardName = data.default_card_name;
                    if (self.cachedFlatTree) {
                        self.cachedFlatTree.forEach(function(c){
                            if (c.model.name().startsWith(defaultCardName) && c.model.cardid() === card.cardid){
                                if (data.updated_values.node) {
                                    c.model.name(data.updated_values.node.name);
                                    card.name = c.model.name;
                                    c.model.save();
                                }
                            }
                        });
                    }
                    card.parentnodegroupId = _.filter(data.nodegroups, function(ng){return data.updated_values.card.nodegroup_id === ng.nodegroupid;})[0].parentnodegroup_id;
                    self.updateCard(self.topCards(), card, data);
                } else {
                    if (data.updated_values.node.nodegroup_id !== data.updated_values.node.nodeid) {
                        var oldCard = _.find(self.flattenTree(self.topCards(), []), function(card) {
                            return card.nodegroupid === data['updated_values'].node.nodeid;
                        });
                        if (oldCard) {
                            var parentCards = oldCard.parentCard ? oldCard.parentCard.cards : self.topCards;
                            parentCards.remove(oldCard);
                            parentCards(
                                parentCards().concat(
                                    oldCard.cards()
                                )
                            );
                        }
                    }
                }
                _.each(self.cachedFlatTree, function(cardViewModel) {
                    cardViewModel.dispose();
                });
                self.cachedFlatTree = self.flattenTree(self.topCards(), []);
                _.each(self.cachedFlatTree, function(node) {
                    if (node.nodegroupid === selectedNodegroupId) {
                        self.collapseAll();
                        self.multiselect ? self.selection([node]) : self.selection(node);
                        self.expandToRoot(node);
                    }
                });
            },
            deleteCard: function(selectedNodegroupId) {
                removeCard(self.topCards, selectedNodegroupId);
                if (self.topCards().length){ self.topCards()[0].selected(true); }
            },
            addCard: function(data, parentcards, parent) {
                if (!parentcards) {
                    parentcards = self.topCards;
                }
                self.graphModel.set('nodegroups', self.graphModel.get('nodegroups').concat([data.nodegroup]));
                var newCardViewModel = new CardViewModel({
                    card: data.card,
                    graphModel: self.graphModel,
                    tile: null,
                    resourceId: ko.observable(),
                    displayname: ko.observable(),
                    handlers: {},
                    cards: cardList,
                    tiles: [],
                    selection: selection,
                    hover: hover,
                    scrollTo: scrollTo,
                    multiselect: self.multiselect,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: null,
                    cardwidgets: data.cardwidgets,
                    userisreviewer: true,
                    perms: ko.observableArray(),
                    permsLiteral: ko.observableArray(),
                    parentCard: parent,
                    constraints: getBlankConstraint(data.card),
                    topCards: self.topCards,
                });
                parentcards.push(newCardViewModel);

                var node = _.find(self.graphModel.get('nodes')(), function(node) {
                    return node.nodeid === data.card.nodegroup_id;
                });
                self.graphModel.getChildNodesAndEdges(node).nodes.forEach(function(node) {
                    var card = _.find(ko.unwrap(parentcards), function(card) {
                        return card.nodegroupid === (ko.unwrap(node.nodeGroupId) ||
                            ko.unwrap(node.nodegroup_id)) &&
                            card.model.cardid() !== newCardViewModel.model.cardid();
                    });
                    if (card) {
                        parentcards.remove(card);
                        var cardIDs = newCardViewModel.cards().map(function(card) {
                            return card.cardid;
                        });
                        if (!_.contains(cardIDs, card.cardid)) {
                            newCardViewModel.cards.push(card);
                        }
                    }
                });

                if (_.contains(_.keys(this.nodeLookup), node.nodeid) === false) {
                    this.nodeLookup[node.nodeid] = node;
                }

                self.cachedFlatTree = self.flattenTree(self.topCards(), []);
                return newCardViewModel;
            },
            reorderCards: function() {
                loading(true);
                var cards = _.map(self.topCards(), function(card, i) {
                    card.model.get('sortorder')(i);
                    return {
                        id: card.model.id,
                        name: card.model.get('name')(),
                        sortorder: i
                    };
                });
                $.ajax({
                    type: 'POST',
                    data: JSON.stringify({
                        cards: cards
                    }),
                    url: arches.urls.reorder_cards,
                    complete: function() {
                        loading(false);
                    }
                });
            },
            selection: selection,
            filter: filter,
            isFuncNode: function() {
                var nodegroupId = null, pdFunction = this.primaryDescriptorFunction;

                // params.card always seems to be undefined...
                if (params.card && pdFunction) {
                    // console.log(ko.unwrap(params));
                    nodegroupId = params.card.nodegroup_id;

                    for (var descriptor in ['name', 'description'])
                    {
                        try {
                            if (nodegroupId === pdFunction['config']['descriptor_types'][descriptor]['nodegroup_id'])
                                return true;
                        } catch (e) {
                            // Descriptor doesn't exist so ignore the exception
                            console.log("No descriptor configuration for "+descriptor);
                        }
                    }
                    return false;
                }
            }
        });

        this.topCards = ko.observableArray();

        var tc = _.filter(data.cards, function(card) {
            var nodegroup = _.find(ko.unwrap(params.graphModel.get('nodegroups')), function(group) {
                return ko.unwrap(group.nodegroupid) === card.nodegroup_id;
            });
            return !nodegroup || !ko.unwrap(nodegroup.parentnodegroup_id);
        });
        this.topCards(tc.map(function(card) {
            var constraints =  data.constraints.filter(function(ct){return ct.card_id === card.cardid;});
            if (constraints.length === 0) {
                constraints = getBlankConstraint(card);
            }
            return new CardViewModel({
                card: card,
                appliedFunctions: params.appliedFunctions(),
                primaryDescriptorFunction: params.primaryDescriptorFunction(),
                graphModel: params.graphModel,
                tile: null,
                resourceId: ko.observable(),
                displayname: ko.observable(),
                handlers: {},
                cards: data.cards,
                constraints: constraints,
                tiles: [],
                selection: selection,
                hover: hover,
                scrollTo: scrollTo,
                multiselect: self.multiselect,
                loading: loading,
                filter: filter,
                provisionalTileViewModel: null,
                cardwidgets: data.cardwidgets,
                userisreviewer: true,
                perms: ko.observableArray(),
                permsLiteral: ko.observableArray(),
                topCards: self.topCards
            });
        }));


        var topCard = self.topCards()[0];
        if (topCard != null) {
            if (self.multiselect === true) {
                selection.push(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);
            } else {
                selection(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);
            }
        }

        self.graphModel.get('cards').subscribe(function(graphCards) {
            var currentCards = self.flattenTree(self.topCards(), []);
            var cardIds = currentCards.map(function(card) {
                return card.model.cardid();
            });
            var newCards = graphCards.filter(function(card) {
                return !_.contains(cardIds, card.cardid);
            });
            cardList = cardList.concat(newCards);

            newCards.forEach(function(card) {
                var nodegroup = _.find(ko.unwrap(params.graphModel.get('nodegroups')), function(group) {
                    return ko.unwrap(group.nodegroupid) === card.nodegroup_id;
                });
                var parent = _.find(currentCards, function(currentCard) {
                    return currentCard.nodegroupid === nodegroup.parentnodegroup_id;
                });
                if (parent || !nodegroup.parentnodegroup_id) {
                    self.addCard({
                        nodegroup: nodegroup,
                        card: card,
                        cardwidgets: self.graphModel.get('cardwidgets')
                    }, parent ? parent.cards : self.topCards, parent);
                }
            });
        });
    };
    return CardTreeViewModel;
});
