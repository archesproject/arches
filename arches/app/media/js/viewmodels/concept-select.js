define([
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
], function(ko, $, WidgetViewModel, arches) {
    var NAME_LOOKUP = {};

    var ConceptSelectViewModel = function(params) {
        var self = this;

        params.configKeys = ['placeholder', 'defaultValue'];
        
        this.multiple = params.multiple || false;
        this.allowClear = true;
        this.displayName = ko.observable('');

        WidgetViewModel.apply(this, [params]);

        this.valueList = ko.computed(function() {
            var valueList = self.value() || self.defaultValue();
            self.displayName();
            
            if (!self.multiple && valueList) {
                valueList = [valueList];
            }
            if (Array.isArray(valueList)) {
                return valueList;
            }
            return [];
        });

        this.valueObjects = ko.computed(function() {
            self.displayName();
            return self.valueList().map(function(value) {
                return {
                    id: value,
                    name: NAME_LOOKUP[value]
                };
            }).filter(function(item) {
                return item.name;
            });
        });

        this.displayValue = ko.computed(function() {
            var val = self.value();
            var name = self.displayName();
            var displayVal = null;

            if (val) {
                displayVal = name;
            }

            return displayVal;
        });

        this.setNames = function() {
            var names = [];
            self.valueList().forEach(function(val) {
                if (ko.unwrap(val)) {
                    if (NAME_LOOKUP[val]) {
                        names.push(NAME_LOOKUP[val]);
                        self.displayName(names.join(', '));
                    } else {
                        $.ajax(arches.urls.get_pref_label + '?valueid=' + ko.unwrap(val), {
                            dataType: "json"
                        }).done(function(data) {
                            NAME_LOOKUP[val] = data.value;
                            names.push(data.value);
                            self.displayName(names.join(', '));
                        });
                    }
                }
            });
        };
        this.setNames();

        this.value.subscribe(function() {
            self.setNames();
        });

        this.select2Config = {
            value: self.value,
            clickBubble: true,
            multiple: self.multiple,
            closeOnSlect: false,
            placeholder: self.placeholder,
            allowClear: true,
            ajax: {
                url: arches.urls.paged_dropdown,
                dataType: 'json',
                quietMillis: 250,
                data: function(term, page) {
                    return {
                        conceptid: ko.unwrap(params.node.config.rdmCollection),
                        query: term,
                        page: page
                    };
                },
                results: function(data) {
                    data.results.forEach(function(result) {
                        if (result.collector) {
                            delete result.id;
                        }
                    });
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
                    indentation += '&nbsp;&nbsp;&nbsp;&nbsp;';
                }
                return indentation + item.text;
            },
            formatSelection: function(item) {
                return item.text;
            },
            clear: function() {
                self.value('');
            },
            isEmpty: ko.computed(function() {
                return self.value() === '' || !self.value();
            }),
            initSelection: function(el, callback) {
                var valueList = self.valueList();
                
                var setSelectionData = function(data) {
                    var valueData;

                    if (self.multiple) {
                        if (!(data instanceof Array)) { data = [data]; }
                        
                        valueData = data.map(function(valueId) {
                            return {
                                id: valueId,
                                text: NAME_LOOKUP[valueId],
                            };
                        });

                        /* add the rest of the previously selected values */ 
                        valueList.forEach(function(value) {
                            if (value !== valueData[0].id) {
                                valueData.push({
                                    id: value,
                                    text: NAME_LOOKUP[value],
                                });
                            }
                        });

                        /* keeps valueData obeying valueList as ordering source of truth */ 
                        if (valueData[0].id !== valueList[0]) {
                            valueData.reverse();
                        }

                    }
                    else {
                        valueData = {
                            id: data,
                            text: NAME_LOOKUP[data],
                        };
                    }

                    if (valueData) { callback(valueData); }
                };

                valueList.forEach(function(value) {
                    if (ko.unwrap(value)) {
                        if (NAME_LOOKUP[value]) {
                            setSelectionData(value);
                        } else {
                            $.ajax(arches.urls.concept_value + '?valueid=' + ko.unwrap(value), {
                                dataType: "json"
                            }).done(function(data) {
                                NAME_LOOKUP[value] = data.value;
                                setSelectionData(value);
                            });
                        }
                    }
                });

            }
        };
    };

    return ConceptSelectViewModel;
});
