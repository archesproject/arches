define([
    'jquery',
    'knockout',
], function($, ko) {
    var DEFAULT_POSITION = { my: 'center top+5', at: 'center bottom', within: 'body' };

    ko.bindingHandlers.tooltip = {
        init: function(element, valueAccessor) {
            var options = ko.unwrap(valueAccessor()) || {};
            options = $.extend(true, { position: DEFAULT_POSITION }, options);
            if (!options.position.within) {
                options.position.within = 'body';
            }
            $(element).tooltip(options);
            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                if ($(element).data('ui-tooltip')) {
                    $(element).tooltip('destroy');
                }
            });
        }
    };
    return ko.bindingHandlers.tooltip;
});
