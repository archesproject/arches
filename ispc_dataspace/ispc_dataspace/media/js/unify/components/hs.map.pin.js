/**
 * PinMap wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSPinMap = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      responsive: true,
      popover: {
        show: false,
        animate: true
      }
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of PinMap wrapper.
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

      this.initPinMap();

      return this.pageCollection;

    },

    initPinMap: function () {
      //Variables
      var $self, config, collection;
      //Variables values
      $self = this;
      config = $self.config;
      collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this;
        //Variables values
        $this = $(el);

        $this.easypinShow(config);

        //Actions
        collection = collection.add($this);
      });
    }

  }

})(jQuery);
