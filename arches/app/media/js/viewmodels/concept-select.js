define([
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
], function(ko, $, WidgetViewModel, arches) {
    var nameLookup = {};
    var ConceptSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder', 'defaultValue'];
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
                    name: nameLookup[value]
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
                        $.ajax(arches.urls.concept_value + '?valueid=' + val, {
                            dataType: "json"
                        }).done(function(data) {
                            nameLookup[val] = data.value;
                            names.push(data.value);
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
            ajax: {
                url: arches.urls.paged_dropdown,
                dataType: 'json',
                quietMillis: 250,
                data: function (term, page) {
                    return {
                        conceptid: ko.unwrap(params.node.config.rdmCollection),
                        query: term,
                        page: page
                    };
                },
                results: function (data, page) {
                    return {
                        results: data.results,
                        more: data.more
                    };
                }
            },
            id: function(item) {
                return item.id;
            },
            formatResult: function(item) {
                var indentation = '';
                for (var i = 0; i < item.depth-1; i++) {
                    indentation += '&nbsp;&nbsp;&nbsp;&nbsp;'
                }
                return indentation + item.text;
            },
            formatSelection: function(item) {
                return item.text;
            },
            initSelection: function(el, callback) {
                var valueList = self.valueList();
                var setSelectionData = function () {
                    var valueData = self.valueObjects().map(function(item) {
                        return {
                            id: item.id,
                            text: item.name
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
                            $.ajax(arches.urls.concept_value + '?valueid=' + value, {
                                dataType: "json"
                            }).done(function(data) {
                                nameLookup[value] = data.value
                                setSelectionData();
                            });
                        }
                    }
                });
            }
        };
    };

    return ConceptSelectViewModel;
});
