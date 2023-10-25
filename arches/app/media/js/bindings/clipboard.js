define([
    'jquery',
    'knockout',
], function($, ko) {
    ko.bindingHandlers.clipboard = {
        init: function(element, valueAccessor) {
            const data = valueAccessor();
            if (data.tooltip) {
                $(element).attr('data-original-title', data.beforeCopiedText)
            }
            function restoreTitle() {
                $(element).tooltip('hide') 
                $(element).attr('data-original-title', data.beforeCopiedText)
                $(element).off('mouseleave', restoreTitle)
            };
            $(element).click(function(){                
                if (data.tooltip) {
                    console.log(data)
                    $(element).attr('data-original-title', data.afterCopiedText)
                    $(element).tooltip('show')
                    $(element).on('mouseleave', restoreTitle)
                }
                navigator.clipboard.writeText(data.value);
            });
        }
    };
    return ko.bindingHandlers.clipboard;
});





