/**
 * Slider wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSSlider = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      dateFormat: 'dd.mm.yy',
      prevText: '<i class="fa fa-angle-left"></i>',
      nextText: '<i class="fa fa-angle-right"></i>'
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Slider wrapper.
     *
     * @param String selector (optional)
     * @param Object config (optional)
     *
     * @return jQuery pageCollection - collection of initialized items.
     */

    init: function (selector, config) {

      this.collection = selector && $(selector).length ? $(selector) : $();
      if (!$(selector).length) return;

      this.config = config && $.isPlainObject(config) ?
          $.extend({}, this._baseConfig, config) : this._baseConfig;

      this.config.itemSelector = selector;

      this.initSlider();

      return this.pageCollection;

    },

    initSlider: function () {
      //Variables
      var $self = this,
          config = $self.config,
          collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this = $(el),
            $resultContainer = $this.data('result-container'),
            rangeBoolean = $this.data('range'),
            minVal = $this.data('min'),
            maxVal = $this.data('max'),
            defaultVal = $this.data('default'),
            step = $this.data('step');

        $this.slider({
          range: rangeBoolean == 1 ? true : 'min',
          min: minVal,
          max: maxVal,
          step: step ? step : 1,
          values: rangeBoolean == 1 ? JSON.parse('[' + defaultVal + ']') : false,
          value: defaultVal ? defaultVal : false,
          slide: function (event, ui) {
            if (rangeBoolean == 1) {
              $('#' + $resultContainer).text(ui.values[0] + ' - ' + ui.values[1]);
            } else {
              $('#' + $resultContainer).text(ui.value);
            }
          }
        });

        if (rangeBoolean == 1) {
          $('#' + $resultContainer).text($this.slider('values', 0) + ' - ' + $this.slider('values', 1));
        }

        //Actions
        collection = collection.add($this);
      });
    }

  };

})(jQuery);
