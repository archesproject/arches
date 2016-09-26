define([
  'jquery',
  'knockout',
  'noUiSlider'
], function ($, ko, noUiSlider) {
    ko.bindingHandlers.noUiSlider = {
      init: function(element, valueAccessor, allBindingsAccesor, viewModel, bindingContext) {
        var model = viewModel;

        noUiSlider.create(element, {
          start: 100,
          range: {
            'min': 0,
            'max': 100
          },
          connect: 'lower'
        });
        element.noUiSlider.on('slide', function(values, handle) {
          var value = values[handle];
          viewModel.handleSlider(value)
        });
      }

    };
    return ko.bindingHandlers.noUiSlider;
});
