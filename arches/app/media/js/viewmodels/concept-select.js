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
        this.allowClear = true;
        this.displayName = ko.observable('');

        WidgetViewModel.apply(this, [params]);

        this.valueList = ko.computed(function() {
            var valueList = self.value();
            
            if (!self.multiple && valueList) {
                valueList = [valueList];
            }
            if (Array.isArray(valueList)) {
                return valueList;
            }
            return [];
        });

        this.valueObjects = ko.computed(function() {
            return self.valueList().map(function(value) {
                return {
                    id: value,
                    name: nameLookup[value]
                };
            }).filter(function(item) {
                return item.name;
            });
        });

        this.updateName = function() {
            var names = [];

            self.valueList().forEach(function(val) {
                if (val) {
                    if (nameLookup[val]) {
                        names.push(nameLookup[val]);
                        self.displayName(names.join(', '));
                    } else {
                        $.ajax(arches.urls.get_pref_label + '?valueid=' + val, {
                            dataType: "json"
                        }).done(function(data) {
                            nameLookup[val] = data.value;
                            names.push(data.value);
                            self.displayName(names.join(', '));
                        });
                    }
                }
            });
        };
        this.value.subscribe(self.updateName);

        this.displayValue = ko.computed(function() {
            var val = self.value();
            var name = self.displayName();
            var displayVal = null;
            
            if (val) {
                displayVal = name;
            }

            return displayVal;
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
                /* reversing the values gives correct ordering if multiple === true */ 
                var valueList = self.valueList().reverse();
                
                var setSelectionData = function(data) {
                    if (!(data instanceof Array)) { data = [data]; }
                    
                    var valueData = data.reduce(function(acc, datum) {
                        var valueDatum;

                        /* coerce different datum types into expected type */ 
                        if (!datum.value) {
                            var valueObject = self.valueObjects().find(function(valueObject) {
                                return valueObject.name === datum;
                            });

                            if (valueObject) {
                                valueDatum = {
                                    id: valueObject.id,
                                    text: valueObject.name,
                                };
                            }
                        }
                        else if (datum.value) {
                            valueDatum = {
                                id: datum.valueid,
                                text: datum.value,
                            };
                        }

                        if (valueDatum) {
                            acc.push(valueDatum);
                        }
                        
                        return acc;
                    }, []);
                    
                    if (self.multiple) {
                        /* add the rest of the valueList */ 
                        valueList.forEach(function(value) {
                            if (value !== valueData[0].id) {
                                valueData.unshift({
                                    id: value,
                                    text: nameLookup[value],
                                });
                            }
                        });
                    }

                    if (valueData) {
                        callback(valueData);
                    }
                };

                valueList.forEach(function(value) {
                    if (value) {
                        if (nameLookup[value]) {
                            setSelectionData(nameLookup[value]);
                        } else {
                            $.ajax(arches.urls.concept_value + '?valueid=' + value, {
                                dataType: "json"
                            }).done(function(data) {
                                nameLookup[value] = data.value;
                                setSelectionData(data);
                            });
                        }
                    }
                });
            }
        };
    };

    return ConceptSelectViewModel;
});
