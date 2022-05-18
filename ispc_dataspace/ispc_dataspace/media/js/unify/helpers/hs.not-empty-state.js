/**
 * Not empty state helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.helpers.HSNotEmptyState = {
    /**
     * Not empty state.
     *
     * @return undefined
     */
    init: function () {
      var collection = $('input:not([type="checkbox"], [type="radio"]), textarea');

      if (!collection.length) return;

      collection.on('keyup', function () {
        var $this = $(this),
            thisVal = $this.val();

        if (thisVal != 0) {
          $this.addClass('g-state-not-empty');
        } else {
          $this.removeClass('g-state-not-empty');
        }
      });
    }
  };
})(jQuery);