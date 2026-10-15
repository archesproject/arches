import $ from 'jquery';
import ko from 'knockout';

ko.bindingHandlers.clipboard = {
    init: function (element, valueAccessor) {
        const data = valueAccessor();
        if (data.tooltip) {
            $(element).attr('data-tooltip', data.beforeCopiedText);
        }

        function resetText() {
            $(element).attr('data-tooltip', data.beforeCopiedText);
            $(element).off('mouseleave', resetText);
        }

        $(element).click(function () {
            if (data.tooltip) {
                $(element).attr('data-tooltip', data.afterCopiedText);
                $(element).on('mouseleave', resetText);
            }
            navigator.clipboard.writeText(ko.unwrap(data.value));
        });
    }
};
ko.bindingHandlers.clipboard.init = ko.bindingHandlers.clipboard.init.bind(ko.bindingHandlers.clipboard);

export default ko.bindingHandlers.clipboard;
