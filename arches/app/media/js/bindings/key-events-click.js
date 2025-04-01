import $ from 'jquery';
import ko from 'knockout';

// Register binding of onEnterkeyClick. e.g. <div data-bind="onEnterkeyClick"> </div>
ko.bindingHandlers.onEnterkeyClick = {
    init: function (element, valueAccessor) {
        ko.utils.unwrapObservable(valueAccessor()); // Unwrap to get subscription.
        $(element).keypress(function (event) {
            var keyCode = (event.which ? event.which : event.keyCode);
            if (keyCode === 13) {   // Check if keypress is <enter>.
                $(element).click();
            }
            return false;    // Allow default action.
        });
    }
};
ko.bindingHandlers.onEnterkeyClick.init = ko.bindingHandlers.onEnterkeyClick.init.bind(ko.bindingHandlers.onEnterkeyClick);

// Register binding of onSpaceClick. e.g. <div data-bind="onSpaceClick"> </div>
ko.bindingHandlers.onSpaceClick = {
    init: function (element, valueAccessor) {
        ko.utils.unwrapObservable(valueAccessor()); // Unwrap to get subscription.
        $(element).keypress(function (event) {
            var keyCode = (event.which ? event.which : event.keyCode);
            if (keyCode === 32) {   // Check if keypress is <space>.
                $(element).click();
            }
            return false;    // Allow default action.
        });
    }
};
ko.bindingHandlers.onSpaceClick.init = ko.bindingHandlers.onSpaceClick.init.bind(ko.bindingHandlers.onSpaceClick);

export default ko.bindingHandlers;
