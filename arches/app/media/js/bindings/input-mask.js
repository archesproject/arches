// Here's a custom Knockout binding that makes elements shown/hidden via jQuery's fadeIn()/fadeOut() methods
// Could be stored in a separate utility library
define([
  'jquery',
  'knockout',
  'inputmask'
], function ($, ko, inputmask) {
  ko.bindingHandlers.inputmask ={
        init: function (element, valueAccessor) {
            var options = ko.unwrap(valueAccessor());

            var updateMask = function() {
              try {
                 $(element).mask(options.mask());
              } catch (e) {
                 console.log(e)
              }
              if (options.mask() === '') {
                $(element).unmask();
              }
            }

            updateMask();

            if (ko.isObservable(options.mask)) {
                options.mask.subscribe(updateMask);
            }
        }
    };
    return ko.bindingHandlers.inputmask;
});
