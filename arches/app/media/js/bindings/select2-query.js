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
                allowClear: true,
            });
            var value = select2Config.value;
            // select2Config.value = value();

            ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
                $(el).selectWoo('destroy');
                $(el).off("select2:selecting");
                $(el).off("select2:opening");
                $(el).off("change");
            });

            var placeholder = select2Config.placeholder;
            if (ko.isObservable(placeholder)) {
                // placeholder.subscribe(function(newItems) {
                //     select2Config.placeholder = newItems;
                //     $(el).data('renderPlaceholder')();
                // }, this);
                select2Config.placeholder = select2Config.placeholder();
                // if (select2Config.allowClear) {
                //     select2Config.placeholder = select2Config.placeholder === "" ? " " : select2Config.placeholder;
                // }
            }

            var disabled = select2Config.disabled;
            if (ko.isObservable(disabled)) {
                disabled.subscribe(function(isdisabled) {
                    select2Config.disabled = isdisabled;
                    $(el).selectWoo("destroy").selectWoo(select2Config);
                });
                select2Config.disabled = select2Config.disabled();
            }

            $(document).ready(function() {
                $(el).selectWoo(select2Config);
            });

            // this initializes the placeholder for the select element
            // we shouldn't have to do this but there is some issue with selectwoo
            // $(el).data('renderPlaceholder', function(){
            //     var renderedEle = $(el).siblings().first().find('.select2-selection__rendered');
            //     renderedEle.find('.select2-selection__placeholder').remove();
            //     if (renderedEle[0].innerText === ""){
            //         var placeholderHtml = document.createElement("span");
            //         placeholderHtml.classList.add('select2-selection__placeholder');
            //         var placeholderText = document.createTextNode(select2Config.placeholder);
            //         placeholderHtml.appendChild(placeholderText);
            //         renderedEle.append(placeholderHtml);
            //     }
            // });
            // $(el).data('renderPlaceholder')();
            
            if (value) {
                // initialize the dropdown with the value
                //$(el).val(value());

                //select2Config.init(value);

                
                // update the dropdown if something else changes the value
                value.subscribe(function(newVal) {
                    console.log(newVal);
                    // select2Config.value = newVal;
                    // $(el).val(newVal).trigger('change.select2');
                }, this);
            }
            
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

            // $(el).on('select2:selecting', function() {
            //     $(el).trigger('selection:update');
            // });
            
            if (typeof select2Config.onSelect === 'function') {
                $(el).on("select2:selecting", function(e) {
                    select2Config.onSelect(e.params.args.data);
                });
            }
        }
    };

    return ko.bindingHandlers.select2;
});
