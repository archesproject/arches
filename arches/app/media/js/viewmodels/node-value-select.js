define([
    'underscore',
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
], function(_, ko, $, WidgetViewModel, arches) {
    var nameLookup = {};
    var NodeValueSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder'];
        this.multiple = params.multiple || false;

        WidgetViewModel.apply(this, [params]);
        this.resourceinstanceid = params.tile ? params.tile.resourceinstance_id : '';

        this.tiles = ko.observableArray();
        var updateTiles = function() {
            var nodeid = params.node.config.nodeid();
            var resourceId = ko.unwrap(self.resourceinstanceid);
            if (resourceId === '') {
                resourceId = window.location.pathname.split('/');
                resourceId = resourceId[resourceId.length-1]
            };
            var url = arches.urls.resource_tiles.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', resourceId);
            if (nodeid && resourceId) {
                $.ajax({
                    dataType: "json",
                    url: url,
                    data: {
                        nodeid: nodeid
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

        params.node.config.nodeid.subscribe(updateTiles);
        updateTiles();
        if (this.form) {
            this.form.on('after-update', updateTiles);
        }

        this.getSelectedDisplayValue = function() {
            var value = self.value();
            var nodeid = params.node.config.nodeid();
            var tile = _.find(self.tiles(), function (tile) {
                return tile.tileid === value;
            });

            if (tile) {
                return _.find(tile.display_values, function(dv) {
                    return nodeid === dv.nodeid;
                });
            }
        }
        this.displayValue = ko.computed(function() {
            var displayValue = this.getSelectedDisplayValue();
            return displayValue ? displayValue.value : '';
        }, this);

        var getDisplayValueMarkup = function(displayValue) {
            return '<div>' +
                    '<span class="node-value-select-label">' + displayValue.label + '</span>: ' +
                    '<span class="node-value-select-value">' + displayValue.value + '</span>' +
                '</div>';
        };

        this.select2Config = {
            value: this.value,
            clickBubble: true,
            multiple: this.multiple,
            placeholder: this.placeholder,
            allowClear: true,
            query: function (query) {
                var tiles = self.tiles();
                var data = {results: []}
                tiles.forEach(function(tile) {
                    data.results.push(tile);
                });
                query.callback(data);
            },
            initSelection: function(element, callback) {
                var id = $(element).val();
                var tiles = self.tiles();
                if (id !== "") {
                    var setSelection = function (tiles, callback)   {
                        var selection =  _.find(tiles, function (tile) {
                            return tile.tileid === id;
                        });
                        if (selection) {
                            callback(selection);
                        }
                    };
                    if (tiles.length === 0)   {
                        var subscription = self.tiles.subscribe(function (tiles) {
                            setSelection(tiles, callback);
                            subscription.dispose();
                        });
                    } else {
                        setSelection(tiles, callback);
                    }
                }
            },
            escapeMarkup: function (m) { return m; },
            id: function(tile) {
                return tile.tileid;
            },
            formatResult: function(tile) {
                var nodeid = params.node.config.nodeid();
                var nodeDisplayValue = _.find(tile.display_values, function(displayValue) {
                    return nodeid === displayValue.nodeid;
                });
                var markup = '<div class="node-value-select-tile">' +
                    '<div class="selected-node-value">' +
                    getDisplayValueMarkup(nodeDisplayValue) +
                    '</div>';

                tile.display_values.forEach(function(displayValue) {
                    if (nodeid !== displayValue.nodeid) {
                        markup += getDisplayValueMarkup(displayValue);
                    }
                });
                markup += '</div>';
                return markup;
            },
            formatSelection: function(tile) {
                var nodeid = params.node.config.nodeid();
                var displayValue = _.find(tile.display_values, function(dv) {
                    return nodeid === dv.nodeid;
                });
                return displayValue.value;
            }
        };
    };

    return NodeValueSelectViewModel;
});
