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

        this.getPrefLabel = function(labels){
            return koMapping.toJS(labels)?.find(label => label.language===arches.activeLanguage && label.valuetype === 'prefLabel')?.value;
        }; 

        this.displayValue = ko.computed(function() {
            const val = self.value();
            let name = '';
            if (val) {
                name = val.map(item=>self.getPrefLabel(item.labels)).join(", ");
            }
            return val ? name : null;
        });

        this.selectionValue.subscribe(val => {
            if (val) {
                if (!(val instanceof Array)) { val = [val]; }
                const tileReady = val.map(uri => {
                    return {
                        "uri": uri,
                        "listid": NAME_LOOKUP[uri]["listid"],
                        "labels": NAME_LOOKUP[uri].labels
                    };
                });
                self.value(tileReady);
            }
        });

        this.select2Config = {
            value: self.selectionValue,
            clickBubble: true,
            multiple: this.multiple,
            closeOnSelect: true,
            placeholder: self.placeholder,
            allowClear: true,
            ajax: {
                url: arches.urls.controlled_list(ko.unwrap(params.node.config.controlledList)),
                dataType: 'json',
                quietMillis: 250,
                data: function(requestParams) {

                    return {
                        flat: true
                    };
                },
                processResults: function(data) {
                    const items = data.items; 
                    items.forEach(item => {
                        delete item.children;
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
                let indentation = '';
                for (let i = 0; i < item.depth; i++) {
                    indentation += '&nbsp;&nbsp;&nbsp;&nbsp;';
                }

                if (item.uri) {
                    const text = indentation + self.getPrefLabel(item.labels) || arches.translations.searching + '...';
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
                                "prefLabel": self.getPrefLabel(value.labels),
                                "labels": value.labels,
                                "listid": value.listid 
                            };
                    });
       
                    if(!self.select2Config.initComplete){
                        valueData.forEach(function(data) {
                            const option = new Option(
                                self.getPrefLabel(data.labels),
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
