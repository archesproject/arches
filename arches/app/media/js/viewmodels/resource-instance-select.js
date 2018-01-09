define([
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
], function(ko, $, WidgetViewModel, arches) {
    var nameLookup = {};
    var ResourceInstanceSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder'];
        this.multiple = params.multiple || false;

        WidgetViewModel.apply(this, [params]);

        var displayName = ko.observable('');

        this.valueList = ko.computed(function () {
            var valueList = self.value();
            displayName();
            if (!self.multiple && valueList) {
                valueList = [valueList];
            }
            if (Array.isArray(valueList)) {
                return valueList;
            }
            return [];
        });

        this.valueObjects = ko.computed(function () {
            displayName();
            return self.valueList().map(function(value) {
                return {
                    id: value,
                    name: nameLookup[value],
                    reportUrl: arches.urls.resource_report + value
                };
            }).filter(function(item) {
                return item.name;
            });
        });

        var updateName = function() {
            var names = [];
            self.valueList().forEach(function (val) {
                if (val) {
                    if (nameLookup[val]) {
                        names.push(nameLookup[val]);
                        displayName(names.join(', '));
                    } else {
                        $.ajax(arches.urls.resource_descriptors + val, {
                            dataType: "json"
                        }).done(function(data) {
                            nameLookup[val] = data.displayname;
                            names.push(data.displayname);
                            displayName(names.join(', '));
                        });
                    }
                }
            });
        }
        this.value.subscribe(updateName);
        this.displayValue = ko.computed(function() {
            var val = self.value();
            var name = displayName();
            var displayVal = null;

            if (val) {
                displayVal = name;
            }

            return displayVal;
        });
        updateName();

        this.select2Config = {
            value: this.value,
            clickBubble: true,
            multiple: this.multiple,
            placeholder: this.placeholder,
            allowClear: true,
            disabled: this.disabled,
            ajax: {
                url: arches.urls.search_results,
                dataType: 'json',
                quietMillis: 250,
                data: function (term, page) {
                    var graphid = ko.unwrap(params.node.config.graphid);
                    var data = {
                        no_filters: true,
                        page: page
                    };
                    if (graphid && graphid.length > 0) {
                        data.no_filters = false;
                        data.typeFilter = JSON.stringify(
                            graphid.map(function(id) {
                                return {
                                    "graphid": id,
                                    "inverted": false
                                }
                            })
                        );
                    }
                    if (term) {
                        data.no_filters = false;
                        data.termFilter = JSON.stringify([{
                            "inverted": false,
                            "type": "string",
                            "context": "",
                            "context_label": "",
                            "id": term,
                            "text": term,
                            "value": term
                        }]);
                    }
                    return data;
                },
                results: function (data, page) {
                    return {
                        results: data.results.hits.hits,
                        more: data.paginator.has_next
                    };
                }
            },
            id: function(item) {
                return item._id;
            },
            formatResult: function(item) {
                return item._source.displayname;
            },
            formatSelection: function(item) {
                return item._source.displayname;
            },
            initSelection: function(el, callback) {
                var valueList = self.valueList();
                var setSelectionData = function () {
                    var valueData = self.valueObjects().map(function(item) {
                        return {
                            _id: item.id,
                            _source: {
                                displayname: item.name
                            }
                        };
                    });
                    valueData = self.multiple ? valueData : valueData[0];
                    if (valueData) {
                        callback(valueData);
                    }
                };
                valueList.forEach(function(value) {
                    if (value) {
                        if (nameLookup[value]) {
                            setSelectionData();
                        } else {
                            $.ajax(arches.urls.resource_descriptors + value, {
                                dataType: "json"
                            }).done(function(data) {
                                nameLookup[value] = data.displayname
                                setSelectionData();
                            });
                        }
                    }
                });
            }
        };
    };

    return ResourceInstanceSelectViewModel;
});
