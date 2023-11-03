define([
    'jquery',
    'knockout',
], function($, ko) {
    ko.bindingHandlers.clipboard = {
        init: function(element, valueAccessor) {
            const data = valueAccessor();
            if (data.tooltip) {
                $(element).attr('data-original-title', data.beforeCopiedText);
            }
            function resetText() {
                $(element).tooltip('hide');
                $(element).attr('data-original-title', data.beforeCopiedText);
                $(element).off('mouseleave', resetText);
            };
            $(element).click(function(){                
                if (data.tooltip) {
                    $(element).attr('data-original-title', data.afterCopiedText);
                    $(element).tooltip('show');
                    $(element).on('mouseleave', resetText);
                }
                navigator.clipboard.writeText(ko.unwrap(data.value));
            });
        }
    };
    return ko.bindingHandlers.clipboard;
});