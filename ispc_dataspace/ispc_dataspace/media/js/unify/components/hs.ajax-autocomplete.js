/**
 * Ajax autocomplete wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSAjaxAutocomplete = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      animation: 'fade',
      animationSpeed: 400
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Ajax autocomplete wrapper.
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

      this.initAjaxAutocomplete();

      return this.pageCollection;

    },

    initAjaxAutocomplete: function () {
      //Variables
      var $self = this,
          config = $self.config,
          collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this = $(el),
            $target = $this.data('target'),
            animation = $this.data('animation'),
            animationSpeed = $this.data('animation-speed');

        $this.on('keyup', function () {
          if (animation == 'fade') {
            if ($this.val()) {
              $('#' + $target).fadeIn(animationSpeed);
            }

            else {
              $('#' + $target).fadeOut(animationSpeed);
            }
          } else {
            if ($this.val()) {
              $('#' + $target).slideDown(animationSpeed);
            }

            else {
              $('#' + $target).slideUp(animationSpeed);
            }
          }
        });

        $this.on('focusout', function () {
          if (animation == 'fade') {
            $('#' + $target).fadeOut(animationSpeed);
          } else {
            $('#' + $target).slideUp(animationSpeed);
          }
        });

        //Actions
        collection = collection.add($this);
      });
    }

  };

})(jQuery);