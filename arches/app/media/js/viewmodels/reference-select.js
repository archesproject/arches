define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/widget',
], function(ko, $, arches, WidgetViewModel) {
    var NAME_LOOKUP = {};
    var ReferenceSelectViewModel = function(params) {
        var self = this;

        params.configKeys = ['placeholder'];
        this.multiple = !!ko.unwrap(params.node.config.multiValue);
        this.allowClear = true;
        this.displayName = ko.observable('');
        this.options = [];
        this.selectionValue = ko.observable([]);

        WidgetViewModel.apply(this, [params]);
        this.valueList = ko.computed(function() {
            var valueList = self.selectionValue()
            self.displayName();
            if (Array.isArray(valueList)) {
                return valueList;
            }
            return [];
        });

        this.displayValue = ko.computed(function() {
            var val = self.selectionValue();
            var name = self.displayName();
            var displayVal = null;

            if (val) {
                displayVal = name;
            }

            return displayVal;
        });

        this.selectionValue.subscribe(val => {
            if (val) {
                const tileReady = val.map(uri => {
                    const prefLabels = NAME_LOOKUP[uri].labels.reduce((keyObj, valObj) => (keyObj[valObj.language] = valObj.value, keyObj) ,{});
                    return {
                        "uri": uri,
                        "id": NAME_LOOKUP[uri]["listid"],
                        "labels": prefLabels
                    };
                });
                self.value(tileReady);
            }
        });

        this.select2Config = {
            value: self.selectionValue,
            clickBubble: true,
            multiple: true,
            closeOnSelect: true,
            placeholder: self.placeholder,
            allowClear: true,
            ajax: {
                url: arches.urls.controlled_lists,
                dataType: 'json',
                quietMillis: 250,
                data: function(requestParams) {
                    let term = requestParams.term || '';
                    let page = requestParams.page || 1;
                    return {
                        conceptid: ko.unwrap(params.node.config.controlledList),
                        query: term,
                        page: page
                    };
                },
                processResults: function(data) {
                    const items = data.controlled_lists.find(list => list.id === params.node.config.controlledList()).items; 
                    items.forEach(item => {
                        delete item["children"];
                        item["listid"] = item.id;
                        item.id = item.uri;
                    });
                    return {
                        "results": items,
                        "pagination": {
                            "more": false
                        }
                    };
                }
            },
            templateResult: function(item) {
                const indentation = '';
                for (let i = 0; i < item.depth-1; i++) {
                    indentation += '&nbsp;&nbsp;&nbsp;&nbsp;';
                }
                // return indentation + item.text;
                if (item.uri) {
                    const text = item.labels?.find(label => label.language===arches.activeLanguage && label.valuetype === 'prefLabel').value || 'Searching...';
                    NAME_LOOKUP[item.uri] = {"prefLabel": text, "labels": item.labels, "listid": item.listid};
                    return text;
                }
            },
            templateSelection: function(item) {
                return NAME_LOOKUP[item.uri]["prefLabel"];
            },
            escapeMarkup: function(m) { return m; },
            initComplete: false,
            initSelection: function(el, callback) {
                const valueList = self.valueList();
                
                const setSelectionData = function(data) {
                    const valueData = [];

                    if (self.multiple) {
                        if (!(data instanceof Array)) { data = [data]; }
                        
                        valueData = data.map(function(valueId) {
                            return {
                                id: valueId,
                                text: NAME_LOOKUP[valueId]["prefLabel"],
                            };
                        });

                        /* add the rest of the previously selected values */ 
                        valueList.forEach(function(value) {
                            if (value !== valueData[0].id) {
                                valueData.push({
                                    id: value,
                                    text: NAME_LOOKUP[value]["prefLabel"],
                                });
                            }
                        });

                        /* keeps valueData obeying valueList as ordering source of truth */ 
                        if (valueData[0].id !== valueList[0]) {
                            valueData.reverse();
                        }
                    } else {
                        valueData = [{
                            id: data,
                            text: NAME_LOOKUP[data]["prefLabel"],
                        }];
                    }
                    if(!self.select2Config.initComplete){
                        valueData.forEach(function(data) {
                            var option = new Option(data.text, data.id, true, true);
                            $(el).append(option);
                        });
                        self.select2Config.initComplete = true;
                    }
                    self.selectedValues[valueData.id] = valueData;
                    callback(valueData);
                };

                if (valueList.length > 0) {
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
                } else {
                    callback([]);
                }

            }
        };

    };

    return ReferenceSelectViewModel;
});
