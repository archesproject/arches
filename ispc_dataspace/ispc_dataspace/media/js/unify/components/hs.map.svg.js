/**
 * SvgMap wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSSvgMap = {

    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      map: 'world_mill_en',
      zoomOnScroll: false
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of SvgMap wrapper.
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

      this.initSvgMap();

      return this.pageCollection;

    },

    initSvgMap: function () {
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

        $this.vectorMap(config);

        //Actions
        collection = collection.add($this);
      });
    }

  }

})(jQuery);
