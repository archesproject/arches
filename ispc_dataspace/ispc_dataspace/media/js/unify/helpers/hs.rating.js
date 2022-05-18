/**
 * Rating helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.helpers.HSRating = {
    /**
     * Rating.
     *
     * @return undefined
     */
    init: function () {
      var collection = $('.js-rating');

      if (!collection.length) return;

      collection.each(function () {
        var $this = $(this),
          $target = $this.find('> *'),
          hoverClasses = $this.data('hover-classes');

        $target.on('mouseenter', function () {
          $(this).addClass(hoverClasses);
          $(this).prevAll().addClass(hoverClasses);
          $(this).nextAll().not('.click').removeClass(hoverClasses);
        });

        $target.on('mouseleave', function () {
          $target.not('.click').removeClass(hoverClasses);
        });

        $target.on('click', function () {
          $(this).addClass('click ' + hoverClasses);
          $(this).prevAll().addClass('click ' + hoverClasses);
          $(this).nextAll().removeClass('click ' + hoverClasses);
        });
      });
    }
  };
})(jQuery);
