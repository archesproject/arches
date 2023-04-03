define([
    'jquery',
    'knockout',
], function($, ko) {
    // Register binding of onEnterkeyClick. e.g. <div data-bind="onEnterkeyClick"> </div>
    ko.bindingHandlers.onEnterkeyClick = {
        init: function (element, valueAccessor) {
            ko.utils.unwrapObservable(valueAccessor()); // Unwrap to get subscription.
            $(element).keypress(function (event) {
                var keyCode = (event.which ? event.which : event.keyCode);
                if (keyCode === 13) {   // Check if keypress is <enter>.
                    $(element).click();
                }
                return true;    // Allow default action.
            });
        }
    };
    return;
});
