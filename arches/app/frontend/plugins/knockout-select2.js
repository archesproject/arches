define(['jquery', 'knockout', 'underscore', 'select2'], function($, ko, _) {
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var allBindings = allBindingsAccessor().select2;
            var select2Config = ko.utils.unwrapObservable(allBindings.select2Config);
            var value = select2Config.value;

            ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
                $(el).select2('destroy');
            });

            select2Config.formatResult = function(item) {
                return ko.unwrap(item.text);
            };

            function formatData(data) {
                _.each(data, function(item) {
                    if (item.collector === 'collector') {
                        delete item.id;
                    }
                });
            }

            var placeholder = typeof select2Config.placeholder === 'function' ? select2Config.placeholder : ko.observable(select2Config.placeholder);
            placeholder.subscribe(function(newItems) {
                select2Config.placeholder = newItems;
                $(el).select2("destroy").select2(select2Config);
            });
            select2Config.placeholder = placeholder();

            var data = select2Config.data.extend({
                rateLimit: 500
            });
            data.subscribe(function(newItems) {
                formatData(newItems);
                select2Config.data = newItems;
                $(el).select2("destroy").select2(select2Config);
                $(el).select2("val", select2Config.value);
            });

            select2Config.data = select2Config.data();

            formatData(select2Config.data);

            select2Config.createSearchChoice = function(term, data) {
                if ($(data).filter(function() {
                    return ko.unwrap(this.text).localeCompare(term) === 0;
                }).length === 0) {
                    return {
                        id: term,
                        text: term
                    };
                }
            };

            select2Config.getConceptPath = function(rootConceptid) {
                var root = {
                    'children': select2Config.data
                };
                var result = [];
                var isParent = false;

                function lookForChild(obj, conceptid) {
                    isParent = false;
                    _.each(obj.children, function(item) {
                        if (item.conceptid === conceptid) {
                            isParent = true;
                            result.push(obj);
                        }
                    });

                    if (isParent === false) {
                        for (var i = 0; i < obj.children.length; i += 1) {
                            lookForChild(obj.children[i], conceptid);
                        }
                    } else {
                        lookForChild(root, obj.conceptid);
                    }
                }

                lookForChild(root, rootConceptid);

                return result;
            };

            select2Config.formatSelection = function(item) {
                var path = [];
                var result = ko.unwrap(item.text);
                if (select2Config.showParents === true) {
                    path = this.getConceptPath(item.conceptid);
                    if (path.length > 1) {
                        result = ko.unwrap(path[0].text) + ": " + ko.unwrap(item.text);
                    }
                }
                return result;
            };


            select2Config.value = value();
            $(el).select2(select2Config);
            $(el).select2("val", value());
            $(el).on("change", function(val) {
                if (val.val === "") {
                    val.val = null;
                }
                return value(val.val);
            });

            if (ko.unwrap(select2Config.disabled)) {
                $(el).select2("disable");
            }

            $(el).on("select2-opening", function() {
                if (select2Config.clickBubble) {
                    $(el).parent().trigger('click');
                }
            });
            value.subscribe(function(newVal) {
                select2Config.value = newVal;
                $(el).select2("val", newVal);
            }, this);
        }
    };

    return ko.bindingHandlers.select2;
});
