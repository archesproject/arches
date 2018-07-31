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
        this.value = params.value || undefined;
        this.disable = params.disable || function(){return false};
        this.disableMessage = params.disableMessage || '';

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

        var url = ko.observable(arches.urls.search_results)
        this.url = url
        this.select2Config = {
            value: this.value,
            clickBubble: true,
            multiple: this.multiple,
            placeholder: this.placeholder,
            closeOnSelect: false,
            allowClear: true,
            disabled: this.disabled,
            ajax: {
                url: function(){return url()},
                dataType: 'json',
                quietMillis: 250,
                data: function (term, page) {
                    //TODO This regex isn't working, but it would nice fix it so that we can do more robust url checking
                    // var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
                    // var regex = new RegExp(expression);
                    // var isUrl = val.target.value.match(regex)
                    var isUrl = term.startsWith('http');
                    if (isUrl) {
                        url(term.replace('search', 'search/resources'))
                        return {}
                    } else {
                        url(arches.urls.search_results)
                        var graphid = params.node ? ko.unwrap(params.node.config.graphid) : undefined;
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
                    }
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
                if (self.disable(item) === false) {
                    return item._source.displayname;
                } else {
                    return '<span>' + item._source.displayname + ' ' + self.disableMessage + '</span>'
                }
            },
            formatResultCssClass: function(item) {
                if (self.disable(item) === false) {
                    return '';
                } else {
                    return 'disabled'
                }
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
