import ko from 'knockout';
import _ from 'underscore';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import 'bindings/scrollTo';

export default function(params) {
    var self = this;

    if (!params.card && ko.unwrap(params.form.card)) {
        params.card = ko.unwrap(params.form.card);
    }

    this.inResourceEditor = location.pathname.includes(arches.urls.resource_editor);
    this.configKeys = params.configKeys || [];
    this.showIds = params.showIds || false;
    this.state = params.state || 'form';
    this.preview = params.preview;
    this.loading = params.loading || ko.observable(false);
    this.card = params.card;
    this.showGrid = params?.form?.showGrid;
    this.toggleGrid = params?.form?.toggleGrid;
    this.card.hideEmptyNodes = params.hideEmptyNodes;
    this.card.showIds = this.showIds;
    this.tile = params.tile;
    this.reportExpanded = ko.observable(true);
    this.form = params.form;
    this.provisionalTileViewModel = params.provisionalTileViewModel;
    this.reviewer = params.reviewer;
    this.expanded = ko.observable(true);
    this.showHeaderLine = params.showHeaderLine;

    this.config = this.card.model ? this.card.model.get('config') : {};
    _.each(this.configKeys, function(key) {
        self[key] = self.config[key];
    });

    this.showChildCards = ko.computed(function() {
        return this.card.widgets().length === 0;
    }, this);

    this.componentCssClasses = function(widget) {
        return ["card_component",
            ko.unwrap(widget.node?.graph?.attributes?.slug),
            ko.unwrap(widget.node?.alias),
            widget?.widgetLookup[ko.unwrap(widget?.widget_id)].name].join(" ");
    };


    this.initialize = function() {
        self.card.showForm(true);

        self.tiles = ko.computed(function() {
            var tiles = [];
            if (self.tile) {
                return self.getTiles(self.tile);
            } else {
                self.card.tiles().forEach(function(tile) {
                    self.getTiles(tile, tiles);
                });
            }
            return tiles;
        }, self);
        if (ko.isObservable(params.tiles)) {
            params.tiles(self.tiles());

            self.tiles.subscribe(function(tiles) {
                params.tiles(tiles);
            });
        }

        self.cardIdentifier = ko.computed(function() {
            return self.card.model.attributes.source_identifier_id ? self.card.model.attributes.source_identifier_id : self.card.model.nodegroup_id();
        });

        self.widgetNodeIdentifier = function(widget) {
            return ko.unwrap(widget.node.sourceIdentifierId) ? ko.unwrap(widget.node.sourceIdentifierId) : widget.node.id;
        };

        self.dirty = ko.computed(function() {
            if (!ko.unwrap(self.tiles)) {
                return true;
            }
            else {
                return ko.unwrap(self.tiles).reduce(function(acc, tile) {
                    if (tile.dirty()) {
                        acc = true;
                    }
                    return acc;
                }, false);
            }
        });
        if (ko.isObservable(params.dirty)) {
            self.dirty.subscribe(function(dirty) {
                params.dirty(dirty);
            });
        }


        if (self.preview) {
            if (!self.card.newTile) {
                self.card.newTile = self.card.getNewTile();
            }
            self.tile = self.card.newTile;
        }

        if (self.card.tiles().length > 0) {
            self.card.showForm(false);
        }

        if (self.card.preSaveCallback) {
            self.card.preSaveCallback(self.saveTile);
        }
    };

    this.revealForm = function(card){
        if (!card.selected()) {card.selected(true);}
        setTimeout(function(){
            card.showForm(true);
        }, 50);
    };

    this.getTiles = function(tile, tiles) {
        tiles = tiles || [tile];
        tile.cards.forEach(function(card) {
            card.tiles().forEach(function(tile) {
                tiles.push(tile);
                self.getTiles(tile, tiles);
            });
        });
        return tiles;
    };

    this.beforeMove = function(e) {
        e.cancelDrop = (e.sourceParent!==e.targetParent);
    };

    this.startDrag = function(e, ui) {
        ko.utils.domData.get(ui.item[0], 'ko_sortItem').selected(true);
    };

    this.getValuesByDatatype = function(type) {
        var values = {};
        if (self.tile && self.form) {
            var data = self.tile.getAttributes().data;
            _.each(data, function(value, key) {
                var node = self.form.nodeLookup[key];
                if (node && ko.unwrap(node.datatype) === type){
                    values[ko.unwrap(node.id)] = {
                        name: ko.unwrap(node.name),
                        value: value
                    };
                }
            });
        }
        return values;
    };

    this.selectWorkflowTile = function(tile) {  // used for cardinality 'n' cards in workflows
        tile.selected(true);
        self.tile = tile;
        params.dirty(true);
    };

    // ctrl+S to save any edited/dirty tiles in resource view 
    var keyListener = function(e) {
        if (e.ctrlKey && e.key === "s") {
            e.preventDefault();
            if (self?.tile?.dirty() == true && 
                self?.tile?.parent?.isWritable === true) {
                    self.saveTile();
            }
        }
    };
    document.addEventListener("keydown", keyListener)
    // dispose of eventlistener
    this.dispose = function(){
        document.removeEventListener("keydown", keyListener);
    };

    this.saveTile = function(callback) {
        self.loading(true);
        self.tile.transactionId = params.form?.workflowId || undefined;

        if (params.resourceid) {
            self.tile.resourceinstance_id = params.resourceid;
        }
        else if (ko.unwrap(params.form?.resourceId)){
            self.tile.resourceinstance_id = ko.unwrap(params.form.resourceId);
        }
        self.tile.save(function(response) {
            self.loading(false);
            if(params?.form?.error){
                params.form.error(response.responseJSON.message);
            }
            params.pageVm.alert(
                new AlertViewModel(
                    'ep-alert-red',
                    response.responseJSON.title,
                    response.responseJSON.message,
                    null,
                    function(){}
                )
            );
            if (params.form.onSaveError) {
                params.form.onSaveError(self.tile);
            }
        }, function() {
            self.loading(false);
            if (typeof self.onSaveSuccess === 'function') self.onSaveSuccess();
            if (params.form.onSaveSuccess) {
                params.form.onSaveSuccess(self.tile);
            }
            if (typeof callback === 'function') callback();
        });
    };

    var saveTileInWorkflow = function() {
        self.saveTile(function() {
            params.form.complete(true);
        });
    };
    if (params.save) {
        params.save = saveTileInWorkflow;
    }
    if (params.form && params.form.save) {
        params.form.save = saveTileInWorkflow;
    }

    /*
        TODO: Reverse this logic to be in-line with card UX in resource_editor using this logic:
                params.card && params.card.cardinality === 'n'
                && params.form.componentData.cardinalityOverride !== '1'
    */
    if (params.renderContext === 'workflow') {
        if (params.form.componentData.cardinalityOverride === 'n') {
            self.card.selected(true);  // cardinality 'n' cards will display appropriately
            self.inResourceEditor = true;
        }
    }

    this.saveTileAddNew = function() {
        self.saveTile(function() {
            window.setTimeout(function() {
                self.card.selected(true);
            }, 1);
        });
    };

    this.deleteTile = function() {
        params.pageVm.alert(            
            new AlertViewModel(
                'ep-alert-red',
                'Item Deletion.',
                'Are you sure you would like to delete this item?',
                function(){}, //does nothing when canceled
                function() {
                    self.loading(true);
                    self.tile.deleteTile(function(response) {
                        self.loading(false);
                        params.pageVm.alert(
                            new AlertViewModel(
                                'ep-alert-red',
                                response.responseJSON.title,
                                response.responseJSON.message,
                                null,
                                function(){}
                            )
                        );
                        if (params.form.onDeleteError) {
                            params.form.onDeleteError(self.tile);
                        }
                    }, function() {
                        self.loading(false);
                        if (typeof self.onDeleteSuccess === 'function') self.onDeleteSuccess();
                        if (params.form.onDeleteSuccess) {
                            params.form.onDeleteSuccess(self.tile);
                        }
                    });
                })
            );
    };

    this.createParentAndChild = async(parenttile, childcard) => {
        try{
            const newSave = await self.card.saveParentTile(parenttile);
            if(newSave){
                childcard.selected(true);
            }
        } catch (err){
            console.log(err);
        }
    };

    this.initialize();
};
