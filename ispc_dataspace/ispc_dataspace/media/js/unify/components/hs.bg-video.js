/**
 * Background video wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSBgVideo = {
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
     * Initialization of Video and audio wrapper.
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

      this.initBgVideo();

      return this.pageCollection;

    },

    initBgVideo: function () {
      //Variables
      var $this = this,
          collection = $this.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $bgVideo = $(el);

        $bgVideo.hsBgVideo();

        //Add object to collection
        collection = collection.add($bgVideo);
      });
    }
  }

})(jQuery);
