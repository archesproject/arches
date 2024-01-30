define([
    'jquery',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/widget',
], function($, ko, koMapping, arches, WidgetViewModel) {
    var NAME_LOOKUP = {};
    var ReferenceSelectViewModel = function(params) {
        var self = this;

        params.configKeys = ['placeholder'];
        this.multiple = !!ko.unwrap(params.node.config.multiValue);
        this.displayName = ko.observable('');
        this.selectionValue = ko.observable([]); // formatted version of this.value that select2 can use
        this.activeLanguage = arches.activeLanguage;

        WidgetViewModel.apply(this, [params]);

        this.displayValue = ko.computed(function() {
            const val = self.value();
            let name = '';
            if (val) {
                name = val.map(item=>ko.unwrap(item.labels[arches.activeLanguage])).join(", ");
            }
            return val ? name : null;
        });

        this.selectionValue.subscribe(val => {
            if (val) {
                const tileReady = val.map(uri => {
                    const prefLabels = NAME_LOOKUP[uri].labels.reduce((keyObj, valObj) => (keyObj[valObj.language] = valObj.value, keyObj), {});
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
                        delete item["children"]; // 'children' property forces select2 to use its own grouping. We don't want that right now
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
                // TODO: Support nested items with indentation
                // const indentation = '';
                // for (let i = 0; i < item.depth-1; i++) {
                //     indentation += '&nbsp;&nbsp;&nbsp;&nbsp;';
                // }
                // return indentation + item.text;
                if (item.uri) {
                    const text = item.labels?.find(label => label.language===arches.activeLanguage && label.valuetype === 'prefLabel').value || 'Searching...';
                    NAME_LOOKUP[item.uri] = {"prefLabel": text, "labels": item.labels, "listid": item.listid};
                    return text;
                }
            },
            templateSelection: function(item) {
                if (!item.uri) { // option has a different shape when coming from initSelection vs templateResult
                    return item.text; 
                } else {
                    return NAME_LOOKUP[item.uri]["prefLabel"];
                }
            },
            escapeMarkup: function(m) { return m; },
            initComplete: false,
            initSelection: function(el, callback) {

                const setSelectionData = function(data) {
                    const valueData = koMapping.toJS(self.value());
                    valueData.forEach(function(value) {
                        NAME_LOOKUP[value.uri] = {
                                "prefLabel": value.labels[arches.activeLanguage],
                                "labels": [value.labels],
                                "listid": value.listid 
                            };
                    });
       
                    if(!self.select2Config.initComplete){
                        valueData.forEach(function(data) {
                            const option = new Option(
                                data.labels[arches.activeLanguage],
                                data.uri,
                                true, 
                                true
                            );
                            $(el).append(option);
                            self.selectionValue().push(data.uri);
                        });
                        self.select2Config.initComplete = true;
                    }
                    callback(valueData);
                };

                if (self.value()?.length) {
                    setSelectionData();
                } else {
                    callback([]);
                }

            }
        };

    };

    return ReferenceSelectViewModel;
});
