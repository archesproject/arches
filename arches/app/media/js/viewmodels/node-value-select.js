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

        this.tileList = ko.observableArray();
        if (this.form) {
            var updateTileList = function(nodeid) {
                if (nodeid && self.form) {
                    $.ajax({
                        dataType: "json",
                        url: window.location.pathname + '/tiles',
                        data: {
                            nodeid: nodeid
                        },
                        success: function(data) {
                            self.tileList(data.tiles);
                        }
                    });
                }
            };

            params.node.config.nodeid.subscribe(updateTileList);
            updateTileList(params.node.config.nodeid());
            this.form.on('after-update', function (request, tile) {
                updateTileList(params.node.config.nodeid());
            });
        }

        this.select2Config = {
            value: this.value,
            clickBubble: true,
            multiple: this.multiple,
            placeholder: this.placeholder,
            allowClear: true,
            query: function (query) {
                var tileList = self.tileList();
                var data = {results: []}
                tileList.forEach(function(tile) {
                    data.results.push(tile);
                });
                query.callback(data);
            },
            initSelection: function(element, callback) {
                var id = $(element).val();
                var tileList = self.tileList();
                if (id !== "") {
                    var findSelection = function (tileList, callback)   {
                        var selection =  _.find(tileList, function (tile) {
                            return tile.tileid === id;
                        });
                        if (selection) {
                            callback(selection);
                        }
                    };
                    if (tileList.length === 0)   {
                        var subscription = self.tileList.subscribe(function (tileList) {
                            var selection = findSelection(tileList, callback);
                            subscription.dispose();
                        });
                    } else {
                        var selection = findSelection(tileList, callback);
                    }
                }
            },
            // dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
            escapeMarkup: function (m) { return m; },
            id: function(tile) {
                return tile.tileid;
            },
            formatResult: function(tile) {
                return JSON.stringify(tile);
            },
            formatSelection: function(tile) {
                return JSON.stringify(tile);
            },
        };
    };

    return NodeValueSelectViewModel;
});
