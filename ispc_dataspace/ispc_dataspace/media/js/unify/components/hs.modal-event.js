/**
 * Event Modal wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';
  $.HSCore.components.HSModalEvent = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {},

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Modal Event wrapper.
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

      this.initModalEvent();

      return this.pageCollection;
    },

    initModalEvent: function () {
      //Variables
      var $self = this,
        collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this = $(el),
          eventType = $this.data('event-type'); //scrollToSection | callAfterTime

        if (eventType == 'scrollOnce') {
          $self.scrollOnce(el);
        } else if (eventType == 'callAfterTime') {
          $self.callAfterTime(el);
        } else if (eventType == 'scrollSequential') {
          $self.scrollSequential(el);
        } else if (eventType == 'exitIntent') {
          $self.exitIntent(el);
        }

        //Actions
        collection = collection.add($this);
      });
    },
    scrollOnce: function (el) {
      var counter = 0;

      $(window).on('scroll', function () {
        var $this = $(el),
          event = $this.data('event'),
          thisOffsetTop = $this.offset().top;

        if (counter == 0) {
          if ($(window).scrollTop() >= thisOffsetTop) {
            counter += 1;

            eval(event);
          }
        }
      });
    },
    scrollSequential: function (el) {
      var counter = 0;

      $(window).on('scroll', function () {
        var $this = $(el),
          eventFirst = $this.data('event-first'),
          eventSecond = $this.data('event-second'),
          thisOffsetTop = $this.offset().top;

        if (counter == 0) {
          if ($(window).scrollTop() >= thisOffsetTop) {
            counter += 1;

            eval(eventFirst);
          }
        } else if (counter == 1) {
          if ($(window).scrollTop() < thisOffsetTop) {
            counter -= 1;

            eval(eventSecond);
          }
        }
      });
    },
    callAfterTime: function (el) {
      var $this = $(el),
        event = $this.data('event'),
        time = $this.data('time');

      setTimeout(function () {
        eval(event);
      }, time);
    },
    exitIntent: function (el) {
      var $this = $(el),
        event = $this.data('event');

      $('html').mouseleave(function () {
        eval(event);

        $('html').unbind('mouseleave');
      });
    }
  };
})(jQuery);
