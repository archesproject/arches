/**
 * Height calculating helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.helpers.HSHeightCalc = {
    /**
     * Rating.
     *
     * @return undefined
     */
    init: function () {
      var collection = $('[data-calc-target]');

      if (!collection.length) return;

      collection.each(function () {
        var $this = $(this),
          $target = $this.data('calc-target');
        $this.css({
          'height': 'calc(100vh - ' + $($target).outerHeight() + 'px)',
        });
      });
    }
  };
})(jQuery);
