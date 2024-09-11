define([
    'jquery',
    'knockout',
    'underscore',
    'select-woo'
], function($, ko, _) {
    ko.bindingHandlers.select2Query = {
        init: function(el, valueAccessor, allBindingsAccessor) {
            var allBindings = allBindingsAccessor().select2Query;
            var select2Config = ko.utils.unwrapObservable(allBindings.select2Config);
            select2Config = Object.assign({}, select2Config);
            select2Config = _.defaults(select2Config, {
                clickBubble: true,
                multiple: false,
                allowClear: false,
                minimumResultsForSearch: 5
            });
            var value = select2Config.value;
            var attr = allBindingsAccessor()?.attr;
            if(!!attr && Object.hasOwn(attr, 'data-label')){
                el.setAttribute('aria-label', attr['data-label']);
            }

            ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
                try{
                    $(el).selectWoo('destroy');
                }
                catch(e){}
                $(el).off("select2:selecting");
                $(el).off("select2:opening");
                $(el).off("change");
            });

            var placeholder = select2Config.placeholder;
            if (ko.isObservable(placeholder)) {
                const placeholderSubscription = placeholder.subscribe(function(newItems) {
                    select2Config.placeholder = newItems;
                    $(el).selectWoo(select2Config);
                }, this);
                placeholderSubscription.disposeWhenNodeIsRemoved(el);
                select2Config.placeholder = select2Config.placeholder();
                if (select2Config.allowClear) {
                    select2Config.placeholder = select2Config.placeholder === "" ? " " : select2Config.placeholder;
                }
            }

            var disabled = select2Config.disabled;
            if (ko.isObservable(disabled)) {
                const disabledSubscription = disabled.subscribe(function(val) {
                    $(el).prop("disabled", !!val);
                });
                disabledSubscription.disposeWhenNodeIsRemoved(el);
                select2Config.disabled = select2Config.disabled();
            }

            var data = select2Config.data;
            if (ko.isObservable(data)) {
                const dataSubscription = data.subscribe(function(data) {
                    var currentSelection = $(el).select2('data').map(selected => selected.id);
                    $(el).find("option").remove();
                    data.forEach(data => {
                        // add new options to the dropdown
                        if ($(el).find("option[value='" + data.id + "']").length === 0) {
                            // Create a DOM Option and pre-select by default
                            var newOption = new Option(data.text, data.id, false, false);
                            // Append it to the select
                            $(el).append(newOption);
                        } 
                    });
                    // maintain the current selection after adding new dropdown options
                    $(el).val(currentSelection).trigger('change');
                });
                dataSubscription.disposeWhenNodeIsRemoved(el);
                select2Config.data = select2Config.data();
            }

            // this initializes the placeholder for the single select element
            // we shouldn't have to do this but there is some issue with selectwoo
            // specifically rendering the placeholder for resource instance widgets in adv. search
            var renderPlaceholder = function() {
                var renderedEle = $(el).siblings().first().find('.select2-selection__rendered');
                var placeholderEle = renderedEle.find('.select2-selection__placeholder');
                if (placeholderEle[0]?.innerText === "" && !select2Config.multiple){
                    placeholderEle.remove();
                    var placeholderHtml = document.createElement("span");
                    var placeholderText = document.createTextNode(select2Config.placeholder);
                    placeholderHtml.classList.add('select2-selection__placeholder');
                    placeholderHtml.appendChild(placeholderText);
                    renderedEle.append(placeholderHtml);
                }
            };

            $(document).ready(function() {
                $(el).selectWoo(select2Config);
                
                if (value) {
                    value.extend({ rateLimit: 100 });
                    // initialize the dropdown with the value
                    $(el).val(value());
                    $(el).trigger('change.select2'); 
    
                    // update the dropdown if something else changes the value
                    const valueSubscription = value.subscribe(function(newVal) {
                        //console.log(newVal);
                        // select2Config.value = newVal;
                        $(el).val(newVal);
                        $(el).trigger('change.select2');

                        if(!newVal){
                            window.setTimeout(function(){
                                renderPlaceholder();
                            },300);
                        }
                    }, this);
                    valueSubscription.disposeWhenNodeIsRemoved(el);
                }
                window.setTimeout(function(){
                    renderPlaceholder();
                },300);
            });

            
            $(el).on("change", function(e) {
                let val = $(el).val();
                if (val === "") {
                    val = null;
                }
                value(val);
            });
            
            $(el).on("select2:opening", function() {
                if (select2Config.clickBubble) {
                    $(el).parent().trigger('click');
                }
            });
            
            if (typeof select2Config.onSelect === 'function') {
                $(el).on("select2:selecting", function(e) {
                    select2Config.onSelect(e.params.args.data);
                });
            }
        }
    };

    return ko.bindingHandlers.select2;
});
