define([
    'jquery',
    'knockout',
], function($, ko) {
    ko.bindingHandlers.clipboard = {
        init: function(element, valueAccessor) {
            var value = valueAccessor();
            var input = $(element).find('input'); // an input or textarea is needed for copying to clipboard
            input = $(element).find('textarea');
            if (input.length === 0) { // if there's no input or textarea in the element, we'll create a tempoarary one and copy the value from it
                $(element).click(function(){
                    var html = '<input value="' + ko.unwrap(value) + '"></input>';
                    $(element).append(html);
                    var tempInput = $(element).find('input');
                    tempInput[0].select();
                    window.document.execCommand("copy");
                    tempInput.remove('input');
                });
            } else {
                $(element).click(function(){
                    input.select();
                    window.document.execCommand("copy");
                });
            }
        }
    };
    return ko.bindingHandlers.clipboard;
});