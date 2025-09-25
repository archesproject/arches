import ko from 'knockout';
import $ from 'jquery';
import _ from 'underscore';
import arches from 'arches';
import WidgetViewModel from 'viewmodels/widget';


var NodeValueSelectViewModel = function(params) {
    var self = this;
    params.configKeys = ['placeholder','displayOnlySelectedNode'];
    this.multiple = params.multiple || false;
        

    WidgetViewModel.apply(this, [params]);
    this.resourceinstanceid = params.tile ? params.tile.resourceinstance_id : '';
    this.tiles = ko.observableArray();

    this.url = function(){
        var resourceId = ko.unwrap(self.resourceinstanceid);
        if (resourceId === '') {
            const splitPath = window.location.pathname.split('/');

            /** 
             * only assign a resourceId if it exists in the database, certain views have URL patterns that match
             * how this component handles Resource logic
            */
            const unsupportedViews = ['add-resource','graph_designer'];
            if (!unsupportedViews.filter(value => splitPath.includes(value)).length) {  
                resourceId = splitPath[splitPath.length-1];
            }
        }
        if (resourceId) {
            return arches.urls.resource_tiles.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', resourceId);
        } else {
            return null;
        }
    };

    this.updateTiles = function(term) {
        var nodeid = params.node.config.nodeid();
        var url = this.url();
        if (nodeid && url) {
            $.ajax({
                dataType: "json",
                url: url,
                data: {
                    nodeid: nodeid,
                    term: term
                },
                success: function(data) {
                    self.tiles(data.tiles);
                },
                error: function(err) {
                    console.log(err, 'unable to fetch tiles');
                }
            });
        }
    };

    this.updateTiles();

    this.toggleDisplayOnlySelected = function(){
        this.displayOnlySelectedNode(!this.displayOnlySelectedNode());
    };

    this.getSelectedDisplayValue = function() {
        var value = self.value();
        var nodeid = params.node.config.nodeid();
        var tile = _.find(self.tiles(), function(tile) {
            return tile.tileid === value;
        });

        if (tile) {
            return _.find(tile.display_values, function(dv) {
                return nodeid === dv.nodeid;
            });
        }
    };
    this.displayValue = ko.computed(function() {
        var displayValue = this.getSelectedDisplayValue();
        return displayValue ? displayValue.value : '';
    }, this);

    var getDisplayValueMarkup = function(displayValue) {
        if (displayValue) {
            return '<div>' +
                    '<span class="node-value-select-label">' + displayValue.label + '</span>: ' +
                    '<span class="node-value-select-value">' + displayValue.value + '</span>' +
                '</div>';
        }
    };

    this.select2Config = {
        value: this.value,
        clickBubble: true,
        multiple: this.multiple,
        placeholder: this.placeholder,
        allowClear: true,
        ajax: {
            dataType: "json",
            url: self.url(),
            data: function(term) {
                return {nodeid: params.node.config.nodeid(), term:term};
            },
            processResults: function(data) {
                var options = [];
                data.tiles.forEach(function(tile) {
                    tile.id = tile.tileid;
                    options.push(tile);
                });
                return { results: options };
            },
            success: function(data) {
                self.tiles(data.tiles);
                return data;
            },
            error: function(err) {
                console.log(err, 'unable to fetch tiles');
            }
        },
        initSelection: function(element, callback) {
            var id = $(element).val();
            var tiles = self.tiles();
            
            // fixes #10027 where inputted values will be reset after navigating away  
            if (self.value()) {
                id = self.value();
            }
            
            if (id !== "") {
                var setSelection = function(tiles, callback)   {
                    var selection =  _.find(tiles, function(tile) {
                        return tile.tileid === id;
                    });
                    if (selection) {
                        callback(selection);
                    }
                };
                if (tiles.length === 0)   {
                    var subscription = self.tiles.subscribe(function(tiles) {
                        setSelection(tiles, callback);
                        subscription.dispose();
                    });
                } else {
                    setSelection(tiles, callback);
                }
            }
        },
        escapeMarkup: function(m) { return m; },
        templateResult: function(tile) {
            var nodeid = params.node.config.nodeid();
            var nodeDisplayValue = _.find(tile.display_values, function(displayValue) {
                return nodeid === displayValue.nodeid;
            });
            if (nodeDisplayValue) {
                var markup = '<div class="node-value-select-tile">' +
                    '<div class="selected-node-value">' +
                    getDisplayValueMarkup(nodeDisplayValue) +
                    '</div>';
                if (!params.config().displayOnlySelectedNode) {
                    tile.display_values.forEach(function(displayValue) {
                        if (nodeid !== displayValue.nodeid) {
                            markup += getDisplayValueMarkup(displayValue);
                        }
                    });}
                markup += '</div>';
                return markup;
            }
        },
        templateSelection: function(tile) {
            var nodeid = params.node.config.nodeid();
            var displayValue = _.find(tile.display_values, function(dv) {
                return nodeid === dv.nodeid;
            });
            return displayValue?.value;
        }
    };
};

export default NodeValueSelectViewModel;
