/**
 * Focus state helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.helpers.HSFocusState = {
    /**
     * Focus state.
     *
     * @return undefined
     */
    init: function () {
      var collection = $('.input-group input:not([type="checkbox"], [type="radio"]), .input-group textarea, .input-group select');

      if (!collection.length) return;

      collection.on('focusin', function () {
        var $this = $(this),
            $thisParent = $this.closest('.input-group');

        $thisParent.addClass('g-state-focus');
      });

      collection.on('focusout', function () {
        var $this = $(this),
            $thisParent = $this.closest('.input-group');

        $thisParent.removeClass('g-state-focus');
      });
    }
  };
})(jQuery);